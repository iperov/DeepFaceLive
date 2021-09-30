import numpy as np

from ..AAxes import AAxes
from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import TransposeInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor

def transpose(input_t : Tensor, axes_order, op_text=None, dtype : np.dtype = None, output_t : Tensor=None, is_add_to_output=False) -> Tensor:
    """
    arguments:

        axes_order     Int
                       Iterable of ints
                       None

        dtype           cast to dtype

        op_text(None)    optional op with value during transpose.
                        'O = I'

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size

    """
    op = SCacheton.get(_TransposeOp, input_t.shape, input_t.dtype, dtype, AAxes(axes_order), op_text, False if output_t is None else is_add_to_output )

    if output_t is None:
        output_t = Tensor (op.o_shape, op.o_dtype, device=input_t.get_device())
    elif output_t.shape.size != op.o_shape.size:
        raise ValueError(f'output_t must have size {op.o_shape.size}')

    input_t.get_device().run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer() )

    return output_t


class _TransposeOp:
    def __init__(self, i_shape : AShape, i_dtype : np.dtype, o_dtype : np.dtype, axes_order : AAxes, op_text, is_add_to_output : bool ):
        self.axes_order = axes_order
        self.o_shape = o_shape = TransposeInfo(i_shape, axes_order).o_shape
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        if op_text is None:
            op_text = 'O = I'

        self.forward_krn = Kernel(global_shape=(i_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_shape, i_dtype)}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME)
{{

size_t gid = get_global_id(0);

{HKernel.decompose_idx_to_axes_idxs('gid', 'i', i_shape.ndim)}

I_TYPE I = I_GLOBAL_LOAD(gid);
O_TYPE O;

{op_text};

{'O_STORE_ADD' if is_add_to_output else 'O_GLOBAL_STORE'}( O_IDX({HKernel.axes_order_enum('I', axes_order )}), O );

}}""")


