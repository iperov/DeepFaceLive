import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..HType import HType
from ..info import BroadcastInfo, SliceInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def slice_set(input_t : Tensor, slices, value) -> Tensor:
    """
    arguments:

        input_t     input tensor
        slices      argument received from class.__getitem__(slices)
        value


    Remark.

    """
    if HType.is_scalar_type(value):
        v_shape = None
        v_dtype = None
        v_scalar = value
    elif not isinstance(value, Tensor):
        value = Tensor.from_value(value, dtype=input_t.dtype, device=input_t.get_device())
        v_shape = value.shape
        v_dtype = value.dtype
        v_scalar = None

    op = SCacheton.get(_SliceSetOp, input_t.shape, input_t.dtype, v_shape, v_dtype, v_scalar, HType.hashable_slices(slices) )

    if v_scalar is not None:
        input_t.get_device().run_kernel(op.forward_krn, input_t.get_buffer() )
    else:
        input_t.get_device().run_kernel(op.forward_krn, input_t.get_buffer(), value.get_buffer() )

    return input_t

class _SliceSetOp:
    def __init__(self, i_shape : AShape, i_dtype : np.dtype, v_shape : AShape, v_dtype : np.dtype, v_scalar, slices):
        slice_info = SliceInfo(i_shape, slices)

        if v_scalar is None:
            if v_shape.ndim > i_shape.ndim:
                raise ValueError(f'v_shape.ndim {v_shape.ndim} cannot be larger than i_shape.ndim {i_shape.ndim}')

            # Check that v_shape can broadcast with slice_info.shape
            br_info = BroadcastInfo([slice_info.o_shape_kd, v_shape])

            v_br_shape = br_info.br_shapes[1]

        self.forward_krn = Kernel(global_shape=(i_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', i_shape, i_dtype )}

{HKernel.define_tensor('I', v_br_shape, v_dtype ) if v_scalar is None else ''}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME
               {', __global const I_PTR_TYPE* I_PTR_NAME' if v_scalar is None else ''})
{{
size_t gid = get_global_id(0);

{HKernel.decompose_idx_to_axes_idxs('gid', 'O', slice_info.o_shape_kd.ndim)}

if ({' & '.join( [f'o{i} >= {b} & o{i} < {e}' if s != 0 else f'o{i} == {b}' for i, (b,e,s) in enumerate(slice_info.axes_abs_bes)] +
                 [f'((o{i} % {s}) == 0)' for i, (_,_,s) in enumerate(slice_info.axes_abs_bes) if s > 1 ] ) } )

    O_GLOBAL_STORE(gid, {f"I_GLOBAL_LOAD( I_IDX_MOD({HKernel.axes_seq_enum('O', i_shape.ndim)}) ) " if v_scalar is None else f" (O_TYPE)({v_scalar})"} );
}}
""")
