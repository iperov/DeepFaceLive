from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import Conv2DInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def binary_dilate_circle (input_t : Tensor, radius : int = 1, iterations : int = 1, dtype=None):
    """
    Binary dilate operator using circle kernel with radius.

     input_t     Tensor (...,H,W)

    per-element of H,W, set 1 if any neighbor elements inside circle with radius != 0.
    otherwise set 0.
    """
    op = SCacheton.get(_BinaryDilateOp, input_t.shape, input_t.dtype, int(radius), dtype)

    device = input_t.get_device()

    if radius <= 0 or iterations <= 0:
        return input_t.copy()
    else:
        for i in range(iterations):
            if i == 0:
                buf_in = input_t
            else:
                buf_in, buf_out = buf_out, buf_in
            if i <= 1:
                buf_out = Tensor( op.o_shape, op.o_dtype, device=device )
            device.run_kernel(op.forward_krn, buf_out.get_buffer(), buf_in.get_buffer() )

    return buf_out

class _BinaryDilateOp():
    def __init__(self, i_shape : AShape, i_dtype, radius, o_dtype):
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        if i_shape.ndim < 2:
            raise ValueError(f'i_shape.ndim must be >= 2')

        KS = radius*2+1
        IH,IW = i_shape[-2:]

        ci = Conv2DInfo(IH, IW, KS, KS, stride=1, dilation=1, padding='same')

        self.o_shape = o_shape = i_shape

        self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_shape, i_dtype)}

#define PADL {ci.PADL}
#define PADT {ci.PADT}

#define RADIUS {radius}
#define KS {KS}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME)
{{
    size_t gid = get_global_id(0);
    {HKernel.decompose_idx_to_axes_idxs('gid', 'O', o_shape.ndim)}

    {'#pragma unroll' if KS <= 16 else ''}
    for (int kh=0; kh<KS; ++kh)
    {'#pragma unroll' if KS <= 16 else ''}
    for (int kw=0; kw<KS; ++kw)
    {{
        if ( hypot( (float)(kh-RADIUS), (float)(kw-RADIUS) )  <= RADIUS)
        {{
            int im2 = -PADT + kh + om2;
            int im1 = -PADL + kw + om1;

            I_TYPE i_val = (im1 >= 0 & im1 < Im1 & im2 >= 0 & im2 < Im2) ?
                           I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='im2,im1' )}))
                           : 0;

            if (i_val != (I_TYPE)0)
            {{
                O_GLOBAL_STORE(gid, (O_TYPE) 1);
                return;
            }}
        }}
    }}

    O_GLOBAL_STORE(gid, (O_TYPE) 0 );
}}
""")


