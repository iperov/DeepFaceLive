import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HArgs import HArgs
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def matmul(a_t : Tensor, b_t : Tensor, output_t: Tensor=None, is_add_to_output=False) -> Tensor:
    """
    matmul operator in row-major format

     A(...,M,K) x
     B(...,K,N) =
      (...,M,N)

     arguments
        output_t            compute result to this Tensor.
                            Tensor may be with different shape,
                            but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.
    """

    return matmulc(b_t, a_t, output_t=output_t, is_add_to_output=is_add_to_output)



def matmulc(a_t : Tensor, b_t : Tensor, output_t : Tensor = None, is_add_to_output=False) -> Tensor:
    """
    matmul operator in col-major format

        A(...,K,M) x
        B(...,N,K) =
         (...,N,M)

    arguments

        output_t            compute result to this Tensor.
                            Tensor may be with different shape,
                            but should match total size.
                            gradfn will not be set.

        is_add_to_output    add result to output_t if output_t is set.
    """
    device = HArgs.check_get_same_device([a_t, b_t])

    op = SCacheton.get(_MatmulOp, a_t.shape, a_t.dtype, b_t.shape, b_t.dtype, False if output_t is None else is_add_to_output)

    if output_t is None:
        output_t = Tensor (op.o_shape, op.o_dtype, device=device )
    elif output_t.shape.size != op.o_shape.size:
        raise ValueError(f'output_t must have size {op.o_shape.size}')

    device.run_kernel(op.forward_krn, output_t.get_buffer(), a_t.get_buffer(), b_t.get_buffer(), )

    return output_t


class _MatmulOp:
    def __init__(self, a_shape, a_dtype, b_shape, b_dtype, is_add_to_output):
        a_dtype = np.dtype(a_dtype).type
        b_dtype = np.dtype(b_dtype).type

        if a_dtype != np.float32 or b_dtype != np.float32:
            raise ValueError('matmul works only with float32 tensors.')

        if a_shape.ndim != b_shape.ndim:
            raise ValueError(f'ndims are not equal. {a_shape.ndim} != {b_shape.ndim}')

        ndim = a_shape.ndim
        if ndim < 2:
            raise ValueError('Tensors ndim must be at least 2.')

        K, M = a_shape[-2], a_shape[-1]
        N, B_COLS = b_shape[-2], b_shape[-1]

        if K != B_COLS:
            raise ValueError('A_ROWS != B_COLS')

        BATCH = a_shape[0:-2].size
        B_BATCH = b_shape[0:-2].size

        if BATCH != B_BATCH:
            raise ValueError(f'BATCH size {BATCH} != {B_BATCH} in shapes {a_shape} {b_shape}')

        if ndim == 2:
            self.o_shape = AShape( (N, M) )
        else:
            self.o_shape = AShape( a_shape[:-2]+(N, M) )
        self.o_dtype = np.float32

        self.M = M
        self.N = N
        self.K = K

        # Determining optimal tile widths
        for MW in [8,4,2,1]:
            if M % MW == 0:
                break
        for KW in [8,4,2,1]:
            if N % KW == 0 and K % KW == 0:
                break
        NW = KW

        self.forward_krn = Kernel(global_shape=(M//MW, N//NW, BATCH), kernel_text=f"""
#define K {K}
#define N {N}
#define MW {MW}     // M tile Width
#define NW {NW}     // N tile Width  -- NW & KW should be the same !
#define KW {KW}     // K tile Width
#define MT {M//MW}  // MT is max for 'mt' (M tile count)
#define KT {K//KW}  // KT is max for 'kt' (K tile count)

#define floatMW { f'float{MW}' if MW != 1 else 'float'}
#define floatKW { f'float{KW}' if KW != 1 else 'float'}

__kernel void GeMM(__global floatMW* O, const __global floatMW* restrict A, const __global floatKW* restrict B)
{{
    size_t mt = get_global_id(0);    //global M-tile id
    size_t nc = get_global_id(1);    //global N-tile id
    size_t batch = get_global_id(2);

    float AT[KW][MW]; // sub tiles
    float BT[NW][KW];
    float CT[NW][MW];

    #pragma unroll
    for (uint i=0; i<NW*MW; ++i) // zero CT tile
        ((float*) CT)[i] = 0.0;

    for (uint kt=0; kt<KT; ++kt)  // iterate over K-dim tiles
    {{
        #pragma unroll
        for (uint k=0; k<KW; ++k)  // every k-element inside K-dim tile
            *( (floatMW*) AT[k] ) = A[batch*K*MT + (kt*KW + k)*MT + mt]; // store M-Width floats

        #pragma unroll
        for (uint n=0; n<NW; ++n)  // every n-element inside N-dim tile
            *( (floatKW*) BT[n] ) = B[batch*N*KT + (nc*NW + n)*KT + kt]; // store K-Width floats

        #pragma unroll
        for (uint k=0; k<KW; ++k)
        #pragma unroll
        for (uint n=0; n<NW; ++n)  // sub tiles multiplication
        #pragma unroll
        for (uint m=0; m<MW; ++m)
            CT[n][m] += AT[k][m] * BT[n][k];
    }}

    #pragma unroll
    for (uint n=0; n<NW; ++n)
        O[ batch*N*MT + (nc*NW + n)*MT + mt] {'+=' if is_add_to_output else '='}
                               *( (floatMW*) CT[n]);
}}""")

