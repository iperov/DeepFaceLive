from typing import List

import numpy as np

from ..HType import HType
from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import PadInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def pad(input_t : Tensor, axes_paddings : List, mode : str = 'constant', constant_value=0, dtype : np.dtype = None, output_t : Tensor=None) -> Tensor:
    """
    arguments:

        axes_paddings   list of (l_pad, r_pad),

                        if [0] == ... (Ellipsis), then left-side paddings will be filled with (0,0) for remain axes
                        if [-1] == ... , same for ride-side

        dtype           cast to dtype

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size

    """
    op = SCacheton.get(_PadOp, input_t.shape, input_t.dtype, dtype, tuple(axes_paddings), mode, constant_value )

    if output_t is None:
        output_t = Tensor (op.o_shape, op.o_dtype, device=input_t.get_device())
    elif output_t.shape.size != op.o_shape.size:
        raise ValueError(f'output_t must have size {op.o_shape.size}')

    input_t.get_device().run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer() )

    return output_t


class _PadOp:
    def __init__(self, i_shape : AShape, i_dtype : np.dtype, o_dtype : np.dtype, axes_paddings, mode, constant_value ):
        _allow_modes = ['constant']
        if mode not in _allow_modes:
            raise ValueError(f'Allowed pads modes: {_allow_modes}')

        if mode == 'constant':
            if not HType.is_scalar_type(constant_value):
                raise ValueError('constan_value must be scalar')

        info = PadInfo(i_shape, axes_paddings)

        self.o_shape = o_shape = info.o_shape
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_shape, i_dtype)}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME)
{{
size_t gid = get_global_id(0);

{HKernel.decompose_idx_to_axes_idxs('gid', 'O', o_shape.ndim)}

if ({' & '.join(f'o{i} >= {l_pad} & o{i} < (O{i}-{r_pad})'  for i, (l_pad,r_pad) in enumerate(info.axes_paddings))})
    O_GLOBAL_STORE(gid, I_GLOBAL_LOAD( I_IDX({ ','.join(f'o{i}-{l_pad}' for i,(l_pad,r_pad) in zip(range(o_shape.ndim), info.axes_paddings)  ) }) ) );
else
    O_GLOBAL_STORE(gid, (O_TYPE){constant_value} );
    //O_GLOBAL_STORE(gid, I_GLOBAL_LOAD( I_IDX_MOD({ ','.join(f' I{i} + ( (o{i}-{l_pad})*( ((o{i}-{l_pad})/I{i}) % 2 == 0 ? 1: -1) ) % I{i} ' for i,(l_pad,r_pad) in zip(range(o_shape.ndim), info.axes_paddings)  ) }) ) );
}}""")
        #print(self.forward_krn)
