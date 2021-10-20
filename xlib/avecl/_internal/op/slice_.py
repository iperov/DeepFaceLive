from typing import List

import numpy as np

from ..AShape import AShape
from ..AAxes import AAxes
from ..backend import Kernel
from ..HKernel import HKernel
from ..HType import HType
from ..info import SliceInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def split(input_t : Tensor, axis, keepdims=False) -> List[Tensor]:
    """

    arguments

     input_t    Tensor

     axis

    """
    shape = input_t.shape

    result = []
    for i in range(shape[axis]):
        slices = [slice(None, None, None)]*shape.ndim

        slices[axis] = i if not keepdims else slice(i,i+1,1)

        result.append( slice_(input_t, slices) )

    return result


def slice_(input_t : Tensor, slices, dtype : np.dtype = None, output_t=None, is_add_to_output=False) -> Tensor:
    """
    arguments:

        input_t     input tensor
        slices      argument received from class.__getitem__(slices)

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.

    Remark.

    Slicing logic is not the same as numpy:
    For example np[2:0:1] slice will produce invalid array with zero index,
    but nn.slice() will select 2 index, same as val_t[2].
    """
    op = SCacheton.get(_SliceOp, input_t.shape, input_t.dtype, dtype, HType.hashable_slices(slices), False if output_t is None else is_add_to_output )
    o_shape = op.slice_info.o_shape

    if output_t is None:
        if op.slice_info.just_reshaped:
            return input_t.reshape(o_shape)
        else:
            output_t = Tensor(o_shape, op.o_dtype, device=input_t.get_device())

    elif output_t.shape.size != o_shape.size:
        raise ValueError(f'output_t must have size {o_shape.size}')

    input_t.get_device().run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer() )

    return output_t


class _SliceOp:
    def __init__(self, i_shape : AShape, i_dtype : np.dtype, o_dtype : np.dtype, slices, is_add_to_output):
        self.slice_info = slice_info = SliceInfo(i_shape, slices)

        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        self.forward_krn = Kernel(global_shape=(slice_info.o_shape_kd.size,), kernel_text=f"""
{HKernel.define_tensor('O', slice_info.o_shape_kd, o_dtype )}
{HKernel.define_tensor('I', i_shape, i_dtype )}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME)
{{
size_t gid = get_global_id(0);

{HKernel.decompose_idx_to_axes_idxs('gid', 'o', slice_info.o_shape_kd.ndim)}

{chr(10).join( f'size_t i{i} = {b} + o{i} * {s}; ' for i, (b,e,s) in enumerate(slice_info.axes_bes)  )  }

{'O_STORE_ADD' if is_add_to_output else 'O_GLOBAL_STORE'}(gid, I_GLOBAL_LOAD( I_IDX({HKernel.axes_seq_enum('i', i_shape.ndim)}) ) );
}}
""")
