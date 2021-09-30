import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import BroadcastInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor

def remap (input_t : Tensor, coords_t : Tensor, dtype=None) -> Tensor:
    """
    remap input_t in spatial axes using coords_t

    arguments

        input_t     Tensor( ...,IH,IW )

        coords_t    Tensor( ...,OH,OW,D )
                    OH - output height
                    OW - output width
                    D is (2)[x,y] coords

        dtype

    ...-head part of shapes will be broadcasted to each other
    """

    op = SCacheton.get(_RemapOp, input_t.shape, input_t.dtype, coords_t.shape, coords_t.dtype, dtype)

    output_t = Tensor( op.o_shape, op.o_dtype, device=input_t.get_device() )

    input_t.get_device().run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer(), coords_t.get_buffer())

    return output_t


class _RemapOp():
    def __init__(self, i_shape : AShape, i_dtype, c_shape : AShape, c_dtype, o_dtype):
        if np.dtype(i_dtype).type == np.bool_:
            raise ValueError('np.bool_ dtype of i_dtype is not supported.')
        if np.dtype(c_dtype).type == np.bool_:
            raise ValueError('np.bool_ dtype of c_dtype is not supported.')
        if i_shape.ndim < 2:
            raise ValueError('i_shape.ndim must be >= 2 (...,H,W)')
        if c_shape.ndim < 3:
            raise ValueError(f'Coords shape ndim must be >= 3(...,H,W,D)')
        if c_shape[-1] != 2:
            raise ValueError('Last coords dim must be == 2 (x,y)')

        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        if i_shape.ndim == 2 and c_shape.ndim == 3:
            # nothing to broadcast

            i_br_shape = i_shape
            c_br_shape = c_shape

            o_shape = c_shape[-3:-1]
        else:
            op = BroadcastInfo([ i_shape[:-2], c_shape[:-3] ])

            i_br_shape = op.br_shapes[0] + i_shape[-2:]
            c_br_shape = op.br_shapes[1] + c_shape[-3:]

            o_shape = op.o_shape + c_shape[-3:-1]

        self.o_shape = o_shape

        self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""

{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_br_shape, i_dtype)}
{HKernel.define_tensor('C', c_br_shape[:-1], c_dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME, __global const C_PTR_TYPE2* C_PTR_NAME)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'o', o_shape.ndim)}

    C_TYPE2 c_value = C_GLOBAL_LOAD2(C_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim)}));

    float cx01 = (float) c_value.x;
    float cy01 = (float) c_value.y;

    float cx0f = floor(cx01);   int cx0 = (int)cx0f;
    float cy0f = floor(cy01);   int cy0 = (int)cy0f;
    float cx1f = cx0f+1;        int cx1 = (int)cx1f;
    float cy1f = cy0f+1;        int cy1 = (int)cy1f;

    float p00 = I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='cy0,cx0')}));
    float p01 = I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='cy0,cx1')}));
    float p10 = I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='cy1,cx0')}));
    float p11 = I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='cy1,cx1')}));

    p00 *= (cx1f - cx01)*(cy1f - cy01)*(cy0 >= 0 & cy0 < Im2 & cx0 >= 0 & cx0 < Im1);
    p01 *= (cx01 - cx0f)*(cy1f - cy01)*(cy0 >= 0 & cy0 < Im2 & cx1 >= 0 & cx1 < Im1);
    p10 *= (cx1f - cx01)*(cy01 - cy0f)*(cy1 >= 0 & cy1 < Im2 & cx0 >= 0 & cx0 < Im1);
    p11 *= (cx01 - cx0f)*(cy01 - cy0f)*(cy1 >= 0 & cy1 < Im2 & cx1 >= 0 & cx1 < Im1);

    O_GLOBAL_STORE(gid, p00 + p01 + p10 + p11);
}}
""")
