import math

import numpy as np

from ..AAxes import AAxes
from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import ReductionInfo, TransposeInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor
from .slice_ import slice_
from .transpose import transpose
from .any_wise import square, sqrt


def reduce_mean (input_t : Tensor, axes=None, keepdims=False, output_t=None, is_add_to_output=False) -> Tensor:
    """
    Reduce mean operator.

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

        keepdims(False)     keep reduced axes
    """
    return reduce_op ('mean', input_t, axes=axes, keepdims=keepdims, output_t=output_t, is_add_to_output=is_add_to_output)

def reduce_std(input_t, axes=None, keepdims=False):
    """
    Reduce std operator.

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

        keepdims(False)     keep reduced axes
    """
    return sqrt(reduce_variance(input_t, axes, keepdims))


def reduce_variance(input_t, axes=None, keepdims=False):
    """
    Reduce variance operator.

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

        keepdims(False)     keep reduced axes
    """
    mean = reduce_mean(input_t, axes, keepdims=True)
    return reduce_mean(square(input_t - mean), axes, keepdims)

def moments(input_t, axes=None):
    """
    Returns (mean, variance) of input_t

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

    """
    mean = reduce_mean(input_t, axes, True)
    var = reduce_mean(square(input_t - mean), axes, True)
    return mean, var

def reduce_min (input_t : Tensor, axes=None, keepdims=False, output_t=None, is_add_to_output=False) -> Tensor:
    """
    Reduce min operator.

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

        keepdims(False)     keep reduced axes
    """
    return reduce_op ('min', input_t, axes=axes, keepdims=keepdims, output_t=output_t, is_add_to_output=is_add_to_output)

def reduce_max (input_t : Tensor, axes=None, keepdims=False, output_t=None, is_add_to_output=False) -> Tensor:
    """
    Reduce max operator.

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

        keepdims(False)     keep reduced axes
    """
    return reduce_op ('max', input_t, axes=axes, keepdims=keepdims, output_t=output_t, is_add_to_output=is_add_to_output)

def reduce_sum (input_t : Tensor, axes=None, keepdims=False, output_t=None, is_add_to_output=False) -> Tensor:
    """
    Reduce sum operator.

        input_t     Tensor

        axes(None)  int
                    Iterable of ints.
                    None - all axes

        keepdims(False)     keep reduced axes
    """
    return reduce_op ('sum', input_t, axes=axes, keepdims=keepdims, output_t=output_t, is_add_to_output=is_add_to_output)

def reduce_op (op_type : str, input_t, axes=None, keepdims=False, output_t=None, is_add_to_output=False):
    """
    arguments

        op_type             'sum' 'mean' 'min' 'max'

        output_t            compute result to this Tensor.
                            Tensor may be with different shape,
                            but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.
    """

    op = SCacheton.get(_ReduceOp, op_type, input_t.shape, input_t.dtype, AAxes(axes, input_t.shape.ndim), keepdims)

    if output_t is None:
        output_t = Tensor ( op.info.o_shape, input_t.dtype, device=input_t.get_device() )
    elif output_t.shape.size != op.info.o_shape.size:
        raise ValueError(f'output_t must have size {op.info.o_shape.size}')

    # Make an intermediate tensor
    input_t_inter = transpose(input_t, op.intermediate_transpose_axes)

    # Perform multistage inplace operation in intermediate tensor
    for stage, (shape, STAGE_COLS, STAGE_VALID_COLS) in enumerate(zip(op.forward_krn_shapes, op.forward_krn_stage_cols, op.forward_krn_stage_valid_cols)):
        input_t_inter.get_device().run_kernel(op.forward_krn, input_t_inter.get_buffer(), np.int64(op.COLS), np.int64(STAGE_COLS), np.int64(STAGE_VALID_COLS),
                           global_shape=shape)

    if op_type == 'mean':
        # divide values in ROWS by number of COLS
        input_t_inter.get_device().run_kernel(op.mean_div_forward_krn, input_t_inter.get_buffer(), np.int64(op.COLS), global_shape=(op.ROWS,) )

    # Fetch final tensor from zero indexes using slices argument
    slice_(input_t_inter, op.inter_slices, output_t=output_t, is_add_to_output=is_add_to_output)

    return output_t


class _ReduceOp:
    def __init__(self, op_type, i_shape : AShape, i_dtype : np.dtype, axes : AAxes, keepdims=False):
        self.op_type = op_type
        self.info = info = ReductionInfo(i_shape, axes, keepdims)

        # Determine transpose order for intermediate tensor, where reduction axes will be at the end
        self.intermediate_transpose_axes = info.o_axes + info.reduction_axes
        self.intermediate_shape = TransposeInfo(i_shape, self.intermediate_transpose_axes).o_shape

        # slices argument to fetch processed tensor from zero indexes
        self.inter_slices = ( slice(None,None,None), ) * info.o_axes.ndim + (0,) * info.reduction_axes.ndim

        # COLS are reduction axes, ROWS are remaining axes
        rows_ndim = info.o_axes.ndim
        self.ROWS = ROWS = self.intermediate_shape[:rows_ndim].size
        self.COLS = COLS = self.intermediate_shape[rows_ndim:].size

        # Number of stages to operate COLS
        n_stages = (COLS-1).bit_length()
        self.forward_krn_shapes           = [ (ROWS * math.ceil(COLS/ (2**(stage+1)) ),) for stage in range(n_stages) ]
        self.forward_krn_stage_cols       = [ math.ceil(COLS / (2**(stage+1)) ) for stage in range(n_stages) ]
        self.forward_krn_stage_valid_cols = [ math.ceil(COLS / (2** stage   ) ) for stage in range(n_stages) ]

        self.forward_krn = Kernel(f"""
{HKernel.define_tensor('I', (1,), i_dtype)}

__kernel void impl(__global I_PTR_TYPE* I_PTR_NAME, long COLS, long STAGE_COLS, long STAGE_VALID_COLS)
{{
    size_t gid = get_global_id(0);

    size_t col = gid % STAGE_COLS;
    size_t row = gid / STAGE_COLS;
    size_t i_idx = row*COLS + col;

    size_t other_col = col + STAGE_COLS;
    if (other_col < STAGE_VALID_COLS)
    {{
        I_TYPE val_a = I_GLOBAL_LOAD(i_idx);
        I_TYPE val_b = I_GLOBAL_LOAD(row*COLS + other_col);

        {'I_TYPE val_x = val_a + val_b;' if op_type in ['sum','mean'] else
         'I_TYPE val_x = fmin( I_TO_FLOATX(val_a), I_TO_FLOATX(val_b) );' if op_type == 'min' else
         'I_TYPE val_x = fmax( I_TO_FLOATX(val_a), I_TO_FLOATX(val_b) );' if op_type == 'max' else ''
        }
        I_GLOBAL_STORE(i_idx, val_x);
    }}
}}
""")
        self.mean_div_forward_krn = Kernel(f"""
{HKernel.define_tensor('I', (1,), i_dtype)}
__kernel void impl(__global I_PTR_TYPE* I_PTR_NAME, long COLS)
{{
    size_t row = get_global_id(0);
    I_GLOBAL_STORE(row*COLS, I_GLOBAL_LOAD(row*COLS) / COLS );
}}
""")
