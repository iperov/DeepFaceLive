import numpy as np
from typing import List

from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import TileInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor

def tile(input_t : Tensor, tiles : List[int], dtype : np.dtype = None, output_t=None, is_add_to_output=False):
    """
    Tile operator

    arguments

        tiles       Iterable of ints

        dtype

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.
    """

    op = SCacheton.get(_TileOp, input_t.shape, input_t.dtype, tuple(int(tile) for tile in tiles), dtype, False if output_t is None else is_add_to_output)

    if output_t is None:
        output_t = Tensor (op.info.o_shape, op.o_dtype, device=input_t.get_device())
    elif output_t.shape.size != op.info.o_shape.size:
        raise ValueError(f'output_t must have size {op.info.o_shape.size}')

    input_t.get_device().run_kernel( op.forward_krn, output_t.get_buffer(), input_t.get_buffer())

    return output_t

class _TileOp:
    def __init__(self, i_shape : AShape, i_dtype, tiles, o_dtype, is_add_to_output):
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        self.info = info = TileInfo(i_shape, tiles)

        self.forward_krn = Kernel(global_shape=(info.o_shape.size,), kernel_text=f"""

{HKernel.define_tensor('I', i_shape, i_dtype)}
{HKernel.define_tensor('O', info.o_shape, o_dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME)
{{
    size_t gid = get_global_id(0);
    {HKernel.decompose_idx_to_axes_idxs ('gid', 'O', info.o_shape.ndim)}

    {'O_STORE_ADD' if is_add_to_output else 'O_GLOBAL_STORE'} (gid, I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', info.o_shape.ndim)})) );
}}
""")

