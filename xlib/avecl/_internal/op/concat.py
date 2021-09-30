from ..backend import Kernel
from ..HArgs import HArgs
from ..HType import HType
from ..HKernel import HKernel
from ..info import ConcatInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor

def concat(tensor_list, axis, dtype=None, output_t=None, is_add_to_output=False) -> Tensor:
    """
    arguments

        tensor_list     Iterable

        axis            Int

        dtype           np.dtype

        output_t            compute result to this Tensor.
                            Tensor may be with different shape,
                            but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.
    """
    tensor_list = tuple(tensor_list)
    HArgs.check_zero_get_length(tensor_list)
    HArgs.check_all_tensors(tensor_list)

    device = HArgs.check_get_same_device(tensor_list)
    shape_list, dtype_list, _ = HArgs.decompose(tensor_list)

    op = SCacheton.get(_ConcatOp, shape_list, dtype_list, dtype, int(axis), False if output_t is None else is_add_to_output)

    if output_t is None:
        output_t = Tensor (op.info.o_shape, op.o_dtype, device=device)
    elif output_t.shape.size != op.info.o_shape.size:
        raise ValueError(f'output_t must have size {op.info.o_shape.size}')

    for forward_krn,t in zip(op.forward_krns,tensor_list):
        device.run_kernel(forward_krn, output_t.get_buffer(), t.get_buffer(), global_shape=(t.shape.size,) )

    return output_t

class _ConcatOp:
    def __init__(self, shape_list, dtype_list, o_dtype, axis, is_add_to_output):
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else HType.get_most_weighted_dtype (dtype_list)

        self.info = info = ConcatInfo(shape_list, axis)

        self.forward_krns = forward_krns = []

        for i, (shape, dtype) in enumerate(zip(shape_list, dtype_list)):
            forward_krn = Kernel(f"""

{HKernel.define_tensor('O', info.o_shape, o_dtype )}
{HKernel.define_tensor('I', shape, dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'I', shape.ndim)}

    i{info.axis} += {info.axis_offsets[i]};

    {'O_STORE_ADD' if is_add_to_output else 'O_GLOBAL_STORE'}( O_IDX({HKernel.axes_seq_enum('I', info.o_shape.ndim)}), I_GLOBAL_LOAD(gid) );
}}
""")
            forward_krns.append(forward_krn)