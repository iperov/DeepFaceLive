import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..info import BroadcastInfo, Conv2DInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def depthwise_conv2D (input_t : Tensor, kernel_t : Tensor, stride=1, dilation=1, padding='same', dtype=None):
    """
    Depthwise Conv2D operator.

     input_t     Tensor (...,H,W)

     kernel_t    Tensor (...,H,W)

     stride(1)       int

     dilation(1)     int

     padding(same)   'valid'         no padding
                     'same'          output size will be the same
                                     or divided by stride
                     int             padding value for all sides
                     Iterable of 4 ints
                                paddings for left,top,right,bottom sides

    ...-head part of shapes will be broadcasted to each other
    """

    op = SCacheton.get(_DepthwiseConv2DOp, input_t.shape, input_t.dtype, kernel_t.shape, kernel_t.dtype, dtype, int(stride), int(dilation), padding)

    output_t = Tensor( op.o_shape, op.o_dtype, device=input_t.get_device() )
    output_t.get_device().run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer(), kernel_t.get_buffer())

    return output_t

class _DepthwiseConv2DOp():
    def __init__(self, i_shape : AShape, i_dtype, k_shape : AShape, k_dtype, o_dtype, stride, dilation, padding):
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        if i_shape.ndim < 2:
            raise ValueError(f'i_shape.ndim must be >= 2')

        if k_shape.ndim < 2:
            raise ValueError(f'k_shape.ndim must be >= 2')

        IH,IW = i_shape[-2:]
        KH,KW = k_shape[-2:]

        ci = Conv2DInfo(IH, IW, KH, KW, stride, dilation, padding)

        if i_shape.ndim == 2 and k_shape.ndim == 2:
            # nothing to broadcast
            i_br_shape = i_shape
            k_br_shape = k_shape

            o_shape = AShape([ci.OH, ci.OW])
        else:
            op = BroadcastInfo([ i_shape[:-2], k_shape[:-2] ])

            i_br_shape = op.br_shapes[0] + i_shape[-2:]
            k_br_shape = op.br_shapes[1] + k_shape[-2:]

            o_shape = op.o_shape + [ci.OH, ci.OW]

        self.o_shape = o_shape

        self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('I', i_br_shape, i_dtype)}
{HKernel.define_tensor('K', k_br_shape, k_dtype)}

#define PADL {ci.PADL}
#define PADT {ci.PADT}

#define STRIDE {stride}
#define DILATION {dilation}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME, __global const K_PTR_TYPE* K_PTR_NAME)
{{
    size_t gid = get_global_id(0);
    {HKernel.decompose_idx_to_axes_idxs('gid', 'O', o_shape.ndim)}

    float v = 0.0;
    {'#pragma unroll' if KH <= 9 else ''}
    for (int km2=0; km2<Km2; ++km2)
    {{
        int im2 = -PADT + km2*DILATION + om2*STRIDE;
        if (im2 >= 0 & im2 < Im2)
            {'#pragma unroll' if KW <= 9 else ''}
            for (int km1=0; km1<Km1; ++km1)
            {{
                int im1 = -PADL + km1*DILATION + om1*STRIDE;
                if (im1 >= 0 & im1 < Im1)
                    v += ((float)(I_GLOBAL_LOAD(I_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='im2,im1' )}))))
                                 *K_GLOBAL_LOAD(K_IDX_MOD({HKernel.axes_seq_enum('O', o_shape.ndim-2, suffix='km2,km1' )}));
            }}
    }}

    O_GLOBAL_STORE(gid, (O_TYPE) v);
}}
""")


