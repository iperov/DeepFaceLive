import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..EInterpolation import EInterpolation
from ..HKernel import HKernel
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def remap_np_affine (input_t : Tensor, affine_n : np.ndarray, interpolation : EInterpolation = None, inverse=False, output_size=None, post_op_text=None, dtype=None) -> Tensor:
    """
    remap affine operator for all channels using single numpy affine mat

    arguments

        input_t     Tensor (...,H,W)

        affine_n    np.array (2,3)

        interpolation    EInterpolation

        post_op_text    cl kernel
                        post operation with output float value named 'O'
                        example 'O = 2*O;'
        
        output_size     (w,h)
        
        dtype
    """
    if affine_n.shape != (2,3):
        raise ValueError('affine_n.shape must be (2,3)')

    op = SCacheton.get(_RemapAffineOp, input_t.shape, input_t.dtype, interpolation, output_size, post_op_text, dtype)

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
    def __init__(self, i_shape : AShape, i_dtype, interpolation, o_size, post_op_text, o_dtype):
        if np.dtype(i_dtype).type == np.bool_:
            raise ValueError('np.bool_ dtype of i_dtype is not supported.')
        if i_shape.ndim < 2:
            raise ValueError('i_shape.ndim must be >= 2 (...,H,W)')
        if interpolation is None:
            interpolation = EInterpolation.LINEAR

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
        
        if post_op_text is None:
            post_op_text = ''
            
        
        if interpolation == EInterpolation.LINEAR:
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
    
    float O = p00 + p01 + p10 + p11;
    
    {post_op_text}
    
    O_GLOBAL_STORE(gid, O);
}}
""")
        elif interpolation == EInterpolation.CUBIC:
            self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""

{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_shape, i_dtype)}

float cubic(float p0, float p1, float p2, float p3, float x)
{{
    float a0 = p1;
    float a1 = p2 - p0;
    float a2 = 2 * p0 - 5 * p1 + 4 * p2 - p3;
    float a3 = 3 * (p1 - p2) + p3 - p0;
    return a0 + 0.5 * x * (a1 + x * (a2 + x * a3));
}}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME,
                   float a, float b, float c,
                   float d, float e, float f)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'O', o_shape.ndim)}

    float cx01f = om1*a + om2*b + c;
    float cy01f = om1*d + om2*e + f;

    float cxf = floor(cx01f);   int cx = (int)cxf;
    float cyf = floor(cy01f);   int cy = (int)cyf;

    float dx = cx01f-cxf;
    float dy = cy01f-cyf;

    float row[4];

    #pragma unroll
    for (int y=cy-1, j=0; y<=cy+2; y++, j++)
    {{
        float col[4];
        #pragma unroll
        for (int x=cx-1, i=0; x<=cx+2; x++, i++)
        {{
            float sxy = I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='y,x')}));

            col[i] = sxy*(y >= 0 & y < Im2 & x >= 0 & x < Im1);
        }}
        row[j] = cubic(col[0], col[1], col[2], col[3], dx);
    }}

    float O = cubic(row[0], row[1], row[2], row[3], dy);
    {post_op_text}
    O_GLOBAL_STORE(gid, O);
}}
""")
        elif interpolation in [EInterpolation.LANCZOS3, EInterpolation.LANCZOS4]:
            RAD = 3 if interpolation == EInterpolation.LANCZOS3 else 4
            self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""

{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_shape, i_dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME,
                   float a, float b, float c,
                   float d, float e, float f)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'O', o_shape.ndim)}

    float cx01f = om1*a + om2*b + c;
    float cy01f = om1*d + om2*e + f;

    float cxf = floor(cx01f);   int cx = (int)cxf;
    float cyf = floor(cy01f);   int cy = (int)cyf;

    #define RAD {RAD}
    float Fy[2 * RAD];
    float Fx[2 * RAD];

    #pragma unroll
    for (int y=cy-RAD+1, j=0; y<=cy+RAD; y++, j++)
    {{
        float dy = fabs(cy01f - y);
        if (dy < 1e-4) Fy[j] = 1;
        else if (dy > RAD) Fy[j] = 0;
        else Fy[j] = ( RAD * sin(M_PI * dy) * sin(M_PI * dy / RAD) ) / ( (M_PI*M_PI)*dy*dy );
    }}

    #pragma unroll
    for (int x=cx-RAD+1, i=0; x<=cx+RAD; x++, i++)
    {{
        float dx = fabs(cx01f - x);
        if (dx < 1e-4) Fx[i] = 1;
        else if (dx > RAD) Fx[i] = 0;
        else Fx[i] = ( RAD * sin(M_PI * dx) * sin(M_PI * dx / RAD) ) / ( (M_PI*M_PI)*dx*dx );
    }}

    float FxFysum = 0;
    float O = 0;

    #pragma unroll
    for (int y=cy-RAD+1, j=0; y<=cy+RAD; y++, j++)
    #pragma unroll
    for (int x=cx-RAD+1, i=0; x<=cx+RAD; x++, i++)
    {{
        float sxy = I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='y,x')}));

        float Fxyv = Fx[i]*Fy[j];
        FxFysum += Fxyv;

        O += sxy*Fxyv*(y >= 0 & y < Im2 & x >= 0 & x < Im1);
    }}
    O = O / FxFysum;
    {post_op_text}
    O_GLOBAL_STORE(gid, O);
}}
""")
        else:
            raise ValueError(f'Unsupported interpolation type {interpolation}')