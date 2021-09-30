import numpy as np
from typing import List

from ..AShape import AShape
from ..backend import Kernel
from ..HArgs import HArgs
from ..HKernel import HKernel
from ..HType import HType
from ..info import StackInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor

def stack(tensor_list : List[Tensor], axis, dtype=None, output_t=None, is_add_to_output=False):
    """
    Stack operator.

    arguments:

        tensor_list     List of Tensors

        axis            Int

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.
    """
    HArgs.check_zero_get_length(tensor_list)
    HArgs.check_all_tensors(tensor_list)

    device = HArgs.check_get_same_device(tensor_list)

    shape_list, dtype_list, _ = HArgs.decompose(tensor_list)

    op = SCacheton.get(_StackOp, shape_list, dtype_list, int(axis), dtype, False if output_t is None else is_add_to_output)

    if output_t is None:
        output_t = Tensor (op.info.o_shape, op.o_dtype, device=device)
    elif output_t.shape.size != op.info.o_shape.size:
        raise ValueError(f'output_t must have size {op.info.o_shape.size}')

    for i, krn in enumerate(op.forward_krns):
        device.run_kernel(krn, output_t.get_buffer(), tensor_list[i].get_buffer(), np.int64(i) )

    return output_t


class _StackOp:
    def __init__(self, shape_list : List[AShape], dtype_list : List[np.dtype], axis, o_dtype, is_add_to_output):
        self.stack_count = stack_count = len(shape_list)

        i_shape = shape_list[0]
        if not all (s == i_shape for s in shape_list):
            raise ValueError('All shapes must be the same')

        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else HType.get_most_weighted_dtype (dtype_list)
        self.info = info = StackInfo(i_shape, axis, stack_count)

        self.forward_krns = forward_krns = []
        for i_dtype in dtype_list:
            forward_krns.append( Kernel(global_shape=(i_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', info.o_shape, o_dtype )}
{HKernel.define_tensor('I', i_shape, i_dtype )}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME, long i_new_idx)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'I', i_shape.ndim)}

    {'O_STORE_ADD' if is_add_to_output else 'O_GLOBAL_STORE'}( O_IDX({HKernel.axes_seq_enum('I', i_shape.ndim, new_axis=('i_new_idx', info.axis))}), I_GLOBAL_LOAD(gid) );
}}
"""))
