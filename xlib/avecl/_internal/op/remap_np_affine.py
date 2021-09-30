import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..SCacheton import SCacheton
from ..Tensor import Tensor

def remap_np_affine (input_t : Tensor, affine_n : np.array, inverse=False, output_size=None, dtype=None) -> Tensor:
    """
    remap affine operator for all channels using single numpy affine mat

    arguments

        input_t     Tensor (...,H,W)

        affine_n    np.array (2,3)

        dtype
    """
    if affine_n.shape != (2,3):
        raise ValueError('affine_n.shape must be (2,3)')

    op = SCacheton.get(_RemapAffineOp, input_t.shape, input_t.dtype, output_size, dtype)

    output_t = Tensor( op.o_shape, op.o_dtype, device=input_t.get_device() )

    ((a, b, c),
     (d, e, f)) = affine_n
    if not inverse:
        # do inverse by default, match cv2.warpAffine behaviour
        D = a*e - b*d
        D = 1.0 / D if D != 0.0 else 0.0
        a, b, c, d, e, f = (  e*D, -b*D, (b*f-e*c)*D ,
                             -d*D,  a*D, (d*c-a*f)*D )
                             
    input_t.get_device().run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer(),
                                    np.float32(a), np.float32(b), np.float32(c), np.float32(d), np.float32(e), np.float32(f) )

    return output_t


class _RemapAffineOp():
    def __init__(self, i_shape : AShape, i_dtype, o_size, o_dtype):
        if np.dtype(i_dtype).type == np.bool_:
            raise ValueError('np.bool_ dtype of i_dtype is not supported.')
        if i_shape.ndim < 2:
            raise ValueError('i_shape.ndim must be >= 2 (...,H,W)')

        IH,IW = i_shape[-2:]
        if o_size is not None:
            OH,OW = o_size
        else:
            OH,OW = IH,IW

        o_shape = AShape( (OH,OW) )
        if i_shape.ndim > 2:
            o_shape = i_shape[:-2] + o_shape

        self.o_shape = o_shape
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""

{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_shape, i_dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME,
                   float a, float b, float c,
                   float d, float e, float f)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'O', o_shape.ndim)}

    float cx01 = om1*a + om2*b + c;
    float cy01 = om1*d + om2*e + f;

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