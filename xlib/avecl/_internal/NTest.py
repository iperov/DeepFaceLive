import numpy as np

from . import op
from .backend import get_default_device, get_device, set_default_device
from .HType import HType
from .info import Conv2DInfo
from .initializer import InitCoords2DArange, InitRandomUniform
from .NCore import NCore
from .Tensor import Tensor


class NTest():

    def test_all():
        NCore.cleanup()

        prev_device = get_default_device()

        device = get_device(0)
        print(f'Using {device.get_description()}')

        set_default_device(device)

        test_funcs = [
                        InitRandomUniform_test,
                        InitCoords2DArange_test,
                        cast_test,
                        transpose_test,
                        pad_test,
                        concat_test,
                        tile_test,
                        stack_test,
                        slice_test,
                        slice_set_test,
                        reduce_test,
                        matmul_test,
                        any_wise_op_test,
                        depthwise_conv2d_test,
                        remap_np_affine_test,
                        remap_test,
                        warp_affine_test,
                        gaussian_blur_test,
                        binary_erode_circle_test,
                        binary_dilate_circle_test,
                        binary_morph_test,
                        cvt_color_test,
                        rct_test,
                    ]

        for test_func in test_funcs:
            print(f'{test_func.__name__}()')
            test_func()
            device.cleanup()
        device.print_stat()

        NCore.cleanup()

        set_default_device(prev_device)

        print('Done.')

def _all_close(x,y, atol=1, btol=1):
    return np.allclose( np.ndarray.flatten(x[None,...]), np.ndarray.flatten(y[None,...]), atol, btol )

def rct_test():
    for _ in range(10):
      for dtype in [np.float16, np.float32]:
        base_shape = list(np.random.randint(1, 8, size=4) )
        shape = base_shape.copy()
        shape[1] = 3

        mask_shape = base_shape.copy()
        mask_shape[1] = 3

        print(f'rct {shape} {str(np.dtype(dtype).name)} ... ', end='', flush=True)

        source_t = Tensor(shape=shape, dtype=dtype, initializer=InitRandomUniform())
        target_t = Tensor(shape=shape, dtype=dtype, initializer=InitRandomUniform())
        mask_t   = Tensor(shape=mask_shape, dtype=dtype, initializer=InitRandomUniform())

        result_t = op.rct(target_t, source_t, target_mask_t=mask_t, source_mask_t=mask_t )

        print('pass')


def cvt_color_test():
    for _ in range(10):
     for shape_len in range(2,6):
      for in_mode in ['RGB','BGR','XYZ','LAB']:
        for out_mode in ['RGB','BGR','XYZ','LAB']:
          for dtype in [np.float16, np.float32]:
            shape = list(np.random.randint(1, 8, size=shape_len) )

            ch_axis = np.random.randint(len(shape))
            shape[ch_axis] = 3

            print(f'cvt_color {shape} {str(np.dtype(dtype).name)} {in_mode}->{out_mode} ... ', end='', flush=True)

            inp_n = np.random.uniform(size=shape ).astype(dtype)
            inp_t = Tensor.from_value(inp_n)

            out_t = op.cvt_color(inp_t, in_mode=in_mode, out_mode=out_mode, ch_axis=ch_axis)
            inp_t2 = op.cvt_color(out_t, in_mode=out_mode, out_mode=in_mode, ch_axis=ch_axis)

            is_check = in_mode in ['RGB','BGR','XYZ'] and out_mode in ['XYZ','LAB']

            if is_check and not _all_close(inp_t.np(), inp_t2.np(), atol=0.1, btol=0.1):
                raise Exception(f'data is not equal')

            print('pass')

def cast_test():
    for in_dtype in HType.get_np_scalar_types():
        for out_dtype in HType.get_np_scalar_types():
            shape = tuple(np.random.randint(1, 8, size=( np.random.randint(1,5))) )

            print(f'cast: {shape} in_dtype:{str(np.dtype(in_dtype).name)} out_dtype:{str(np.dtype(out_dtype).name)}  ... ', end='', flush=True)

            val_n = np.random.uniform( -64, 64, size=shape ).astype(in_dtype)
            cast_n = val_n.astype(out_dtype)
            val_t = Tensor.from_value(val_n)
            cast_t = op.cast(val_t, out_dtype)

            if not _all_close(cast_t.np(), cast_n):
                raise Exception(f'data is not equal')

            print('pass')

def binary_morph_test():
    for shape_len in range(2,4):
        for dtype in HType.get_np_scalar_types():
            shape = np.random.randint( 1, 64, size=(shape_len,) )
            erode_dilate = np.random.randint( -16, 16 )
            blur = np.random.rand()*16 - 8

            input_n = np.random.randint( 2, size=shape ).astype(dtype)
            input_t = Tensor.from_value(input_n)

            print(f'binary_morph: {shape} erode_dilate:{erode_dilate} blur:{blur} {np.dtype(dtype).name} ... ', end='', flush=True)

            op.binary_morph(input_t, erode_dilate=erode_dilate, blur=blur, fade_to_border=True)

            print('pass')

def binary_erode_circle_test():
    for shape_len in range(2,4):
        for dtype in HType.get_np_scalar_types():

            shape = np.random.randint( 1, 64, size=(shape_len,) )
            radius = np.random.randint( 1, 16 )
            iterations = np.random.randint( 1, 4 )

            input_n = np.random.randint( 2, size=shape ).astype(dtype)
            input_t = Tensor.from_value(input_n)

            print(f'binary_erode_circle: {shape} radius:{radius} iters:{iterations} {np.dtype(dtype).name} ... ', end='', flush=True)

            op.binary_erode_circle(input_t, radius=radius, iterations=iterations)

            print('pass')

def binary_dilate_circle_test():
    for shape_len in range(2,4):
        for dtype in HType.get_np_scalar_types():

            shape = np.random.randint( 1, 64, size=(shape_len,) )
            radius = np.random.randint( 1, 16 )
            iterations = np.random.randint( 1, 4 )

            input_n = np.random.randint( 2, size=shape ).astype(dtype)
            input_t = Tensor.from_value(input_n)

            print(f'binary_dilate_circle: {shape} radius:{radius} iters:{iterations} {np.dtype(dtype).name} ... ', end='', flush=True)

            op.binary_dilate_circle(input_t, radius=radius, iterations=iterations)

            print('pass')


def gaussian_blur_test():
    for shape_len in range(2,5):
        for dtype in [np.float16, np.float32]:

            shape = np.random.randint( 1, 64, size=(shape_len,) )
            sigma = np.random.rand() * 10
            print(f'gaussian_blur: {shape} sigma:{sigma} {np.dtype(dtype).name} ... ', end='', flush=True)

            val_n = np.random.randint( 2**8, size=shape ).astype(dtype)
            val_t = Tensor.from_value(val_n)

            op.gaussian_blur(val_t, sigma)

            print('pass')

def pad_test():
    for iteration in range(1):
      for shape_len in range(5,1,-1):
        for mode in ['constant']:
          for dtype in HType.get_np_scalar_types():
            while True:
                shape = np.random.randint( 1, 8, size=(shape_len,) )

                paddings = tuple( (np.random.randint(8), np.random.randint(8)) for i in range(len(shape)) )

                print(f'pad: {shape} {paddings} {mode} {np.dtype(dtype).name} ... ', end='', flush=True)

                val_n = np.random.randint( 2**8, size=shape ).astype(dtype)
                pad_n = np.pad(val_n, paddings, mode=mode)

                val_t = Tensor.from_value(val_n)
                pad_t = op.pad(val_t, paddings, mode=mode)

                print(f'{pad_n.shape} == {pad_t.shape} ... ', end='', flush=True)

                if pad_n.shape != pad_t.shape:
                    raise Exception(f'shape is not equal')

                if not _all_close(pad_t.np(), pad_n):
                    raise Exception(f'data is not equal')

                print('pass')
                break

def slice_set_test():
    for iteration in [0,1]:
      for shape_len in range(5,1,-1):
          for dtype in HType.get_np_scalar_types():
            while True:
                shape = np.random.randint( 1, 8, size=(shape_len,) )

                if iteration == 0:
                    slices = [ slice(None,None,None), ] * shape_len
                    axis = np.random.randint(shape_len)
                    shape[axis] = 1
                    slices[axis] = 0
                else:
                    slices = []
                    for i in range (shape_len):
                        axis_size = shape[i]

                        b = np.random.randint(axis_size)
                        e = np.random.randint(axis_size)
                        if b == e:
                            slices.append(b)
                        else:
                            if b < e:
                                s = 1
                                if b == 0:
                                    b = None
                                if e == axis_size-1:
                                    e = None
                            else:
                                s = -1
                                if b == axis_size-1:
                                    b = None
                                if e == 0:
                                    e = None
                            slices.append ( slice(b,e,s) )

                    if np.random.randint(2) == 0:
                        axis = np.random.randint(shape_len)
                        slices[axis] = Ellipsis

                shape = tuple(shape)
                slices = tuple(slices)

                print(f'slice_set: {shape} {np.dtype(dtype).name} {slices} ... ', end='', flush=True)

                val_n = np.random.randint( 2**8, size=shape ).astype(dtype)
                val_t = Tensor.from_value(val_n)

                sliced_n = val_n[slices]

                v = [0] if sliced_n.ndim > 0 else 0

                val_n[slices] = v
                val_t[slices] = v

                if not _all_close(val_t.np(), val_n):
                    raise Exception(f'data is not equal')

                print('pass')
                break

def depthwise_conv2d_test():
    def _numpy_depthwise_conv2d(input_n, kernel_n, STRIDE=1, DILATION=1, padding='same', dtype=np.float32):
        N, IC, IH, IW = input_n.shape
        KI, KH, KW = kernel_n.shape

        ci = Conv2DInfo(IH, IW, KH, KW, STRIDE, DILATION, padding)

        PADL, PADT = ci.PADL, ci.PADT

        OC, OH, OW = IC, ci.OH, ci.OW

        O_IK_idxs = { idx:[ [ [], [] ], [ [], [] ] ] for idx in range(OH*OW) }
        K_IO_idxs = { idx:[ [ [], [] ], [ [], [] ] ] for idx in range(KH*KW) }
        I_KO_idxs = { idx:[ [ [], [] ], [ [], [] ] ] for idx in range(IH*IW) }

        for ow in range(OW):
            for oh in range(OH):
                O_idx = oh*OW + ow
                for kh in range(KH):
                    for kw in range(KW):
                        iw = -PADL + kw*DILATION + ow*STRIDE
                        ih = -PADT + kh*DILATION + oh*STRIDE
                        if (iw >= 0) & (ih >= 0) & (iw < IW) & (ih < IH):

                            O_IK_idxs[O_idx][0][0].append (ih)
                            O_IK_idxs[O_idx][0][1].append (iw)
                            O_IK_idxs[O_idx][1][0].append (kh)
                            O_IK_idxs[O_idx][1][1].append (kw)

                            K_idx = kh*KW + kw
                            K_IO_idxs[K_idx][0][0].append (ih)
                            K_IO_idxs[K_idx][0][1].append (iw)
                            K_IO_idxs[K_idx][1][0].append (oh)
                            K_IO_idxs[K_idx][1][1].append (ow)

                            I_idx = ih*IW + iw
                            I_KO_idxs[I_idx][0][0].append (kh)
                            I_KO_idxs[I_idx][0][1].append (kw)
                            I_KO_idxs[I_idx][1][0].append (oh)
                            I_KO_idxs[I_idx][1][1].append (ow)

        output_shape = (N, OC, OH, OW)
        output = np.empty( output_shape, dtype)

        for n in range(N):
            for oc in range(OC):
                for oh in range(OH):
                    for ow in range(OW):
                        O_idx = oh*OW + ow
                        I_idxs = O_IK_idxs[O_idx][0]
                        K_idxs = O_IK_idxs[O_idx][1]

                        v = (  input_n[ n,oc][..., I_idxs[0], I_idxs[1]] *
                            kernel_n [oc][..., K_idxs[0], K_idxs[1]] ).sum()

                        output[n,oc,oh,ow] = v
        return output

    for padding in ['same','valid',2]:
        for dilation in [1,2]:
          for stride in [1,2]:
            for ks in [1,3]:
              for n in [1,4]:
                for ic in [1,4]:
                    for ih,iw in zip(*[[4,16]]*2):
                        if padding == 'valid' and iw < ks:
                            continue
                        for dtype in [np.int16, np.float16, np.float32]:
                            input_shape  = (n, ic, ih, iw)
                            kernel_shape = (ic, ks, ks)

                            print(f'depthwise_conv2d: {input_shape},{kernel_shape},{padding},{stride},{dilation},{np.dtype(dtype).name} ... ', end='', flush=True)

                            input_n  = np.random.randint( 64, size=input_shape ).astype(dtype)
                            kernel_n = np.ones(shape=kernel_shape ).astype(dtype)

                            input_t  = Tensor.from_value(input_n)
                            kernel_t = Tensor.from_value(kernel_n)

                            conved_t = op.depthwise_conv2D(input_t, kernel_t, stride=stride, dilation=dilation, padding=padding)
                            conved_n = _numpy_depthwise_conv2d(input_n, kernel_n, STRIDE=stride, DILATION=dilation, padding=padding, dtype=dtype)

                            if conved_n.shape != conved_t.shape:
                                raise Exception(f'shape is not equal')

                            if not all ( np.ndarray.flatten( conved_t.np() == conved_n) ):
                                raise Exception(f'data is not equal')

                            print('pass')



def warp_affine_test():
    for dtype in HType.get_np_scalar_types():
        if dtype == np.bool_:
            continue
        H = np.random.randint(8, 64)
        W = np.random.randint(8, 64)

        print(f'warp_affine: [{H},{W}] {np.dtype(dtype).name} ... ', end='', flush=True)

        input_t = Tensor ( [H,W,2], dtype, initializer=InitCoords2DArange(0, H-1, 0, W-1) ).sum( (-1,) )

        affine_t = Tensor.from_value ( [[1,0,0],
                                        [0,1,0]], dtype)

        result_t = op.warp_affine(input_t, affine_t)

        if not _all_close(input_t.np(), result_t.np() ):
            raise Exception(f'data is not equal')

        print('pass')


def remap_np_affine_test():
    for dtype in HType.get_np_scalar_types():
        if dtype == np.bool_:
            continue
        H = np.random.randint(8, 64)
        W = np.random.randint(8, 64)

        print(f'remap_np_affine: [{H},{W}] {np.dtype(dtype).name} ... ', end='', flush=True)

        input_t = Tensor ( [H,W,2], dtype, initializer=InitCoords2DArange(0, H-1, 0, W-1) ).sum( (-1,) )

        affine_n = np.array ( [[1,0,0],
                               [0,1,0]], dtype)

        result_t = op.remap_np_affine(input_t, affine_n)

        if not _all_close(input_t.np(), result_t.np() ):
            raise Exception(f'data is not equal')

        print('pass')


def remap_test():
    for dtype in HType.get_np_scalar_types():
        if dtype == np.bool_:
            continue
        H = np.random.randint(8, 64)
        W = np.random.randint(8, 64)

        print(f'remap: [{H},{W}] {np.dtype(dtype).name} ... ', end='', flush=True)

        input_t = Tensor ( [H,W,2], dtype, initializer=InitCoords2DArange(0, H-1, 0, W-1) ).sum( (-1,) )

        coords_t = Tensor ( [H,W,2], dtype, initializer=InitCoords2DArange(0, H-1, 0, W-1) )

        result_t = op.remap(input_t, coords_t)

        if not _all_close(input_t.np(), result_t.np() ):
            raise Exception(f'data is not equal')

        print('pass')

def tile_test():
    for _ in range(3):
      for shape_len in range(3, 5):
        for dtype in HType.get_np_scalar_types():
            shape = tuple(np.random.randint( 8, size=(shape_len,) )+1)
            tiles = tuple(np.random.randint( 4, size=(shape_len,) )+1)

            print(f'tile: {shape} {tiles} {np.dtype(dtype).name} ... ', end='', flush=True)

            val_n = np.random.randint( 2**8, size=shape ).astype(dtype)
            tiled_n = np.tile(val_n, tiles)

            val_t = Tensor.from_value(val_n)
            tiled_t = op.tile(val_t, tiles)

            print(f'{tiled_n.shape} == {tiled_t.shape} ... ', end='', flush=True)

            if tiled_n.shape != tiled_t.shape:
                raise Exception(f'shape is not equal')

            if not _all_close(tiled_t.np(), tiled_n):
                raise Exception(f'data is not equal')

            print('pass')

def stack_test():
    for _ in range(3):
        for shape_len in range(1, 4):
            for dtype in HType.get_np_scalar_types():
                shape = tuple(np.random.randint( 8, size=(shape_len,) )+1)
                axis = np.random.randint(shape_len+1)
                stack_count = np.random.randint(4)+1

                print(f'stack: {shape}*{stack_count} axis:{axis} {np.dtype(dtype).name} ... ', end='', flush=True)

                vals_n = [ np.random.randint( 2**8, size=shape ).astype(dtype) for i in range(stack_count) ]
                stack_n = np.stack(vals_n, axis)

                vals_t = [ Tensor.from_value(vals_n[i]) for i in range(stack_count) ]
                stack_t = op.stack(vals_t, axis)

                print(f'{stack_n.shape} == {stack_t.shape} ... ', end='', flush=True)

                if stack_n.shape != stack_t.shape:
                    raise Exception('shape is not equal')

                if not _all_close(stack_t.np(), stack_n):
                    raise Exception(f'data is not equal')

                print('pass')

def reduce_test():
    for op_type in ['sum', 'mean', 'min', 'max']:
      for dtype in HType.get_np_scalar_types():
        if dtype != np.bool_:
            for shape_len in range(2, 5):
                shape = np.random.randint( 8, size=(shape_len,) )+1

                reduction_axes = np.array([*range(shape_len)])
                np.random.shuffle(reduction_axes)

                # Cut random amount of reduction_axes
                reduction_axes = tuple(reduction_axes [:np.random.randint(shape_len+1)])
                if len(reduction_axes) == 0:
                    reduction_axes = None

                keepdims = np.random.randint(2) == 0

                print(f'reduce {op_type}: {shape} {np.dtype(dtype).name} axes={reduction_axes} keepdims={keepdims} ... ', end='', flush=True)

                if dtype in [np.float16, np.float32]:
                    value_n = np.random.uniform(size=shape).astype(dtype)
                else:
                    value_n = np.random.randint( max(1, int(np.iinfo(dtype).max / np.prod(shape)) ), size=shape, dtype=dtype )

                value_t = Tensor.from_value(value_n)

                if op_type == 'sum':
                    reducted_n = value_n.sum(reduction_axes, keepdims=keepdims)
                    reducted_t = value_t.sum(reduction_axes, keepdims=keepdims)
                elif op_type == 'mean':
                    reducted_n = value_n.mean(reduction_axes, keepdims=keepdims)
                    reducted_t = value_t.mean(reduction_axes, keepdims=keepdims)
                elif op_type == 'max':
                    reducted_n = value_n.max(reduction_axes, keepdims=keepdims)
                    reducted_t = value_t.max(reduction_axes, keepdims=keepdims)
                elif op_type == 'min':
                    reducted_n = value_n.min(reduction_axes, keepdims=keepdims)
                    reducted_t = value_t.min(reduction_axes, keepdims=keepdims)

                print(f'{reducted_n.shape} == {reducted_t.shape} ... ')

                if not _all_close(reducted_t.np(), reducted_n):
                    raise Exception(f'data is not equal')

                print('pass')


def InitRandomUniform_test():
    for dtype in HType.get_np_scalar_types():
        for shape_len in range(1, 5):
            shape = np.random.randint( 8, size=(shape_len,) )+1

            print(f'InitRandomUniform: {shape} {np.dtype(dtype).name} ... ', end='', flush=True)

            Tensor(shape, dtype, initializer=InitRandomUniform()).np()

            print('pass')

def InitCoords2DArange_test():
    for dtype in HType.get_np_scalar_types():
        for shape_len in range(2, 5):
            shape = np.random.randint( 1, 60, size=(shape_len,) ).tolist()
            shape = shape + ([2] if np.random.randint(2) == 0 else [3])
            h_start = np.random.randint(80)
            h_stop = h_start + np.random.randint(80)
            w_start = np.random.randint(80)
            w_stop = w_start + np.random.randint(80)

            print(f'InitCoords2DArange: {shape} {np.dtype(dtype).name} ... ', end='', flush=True)

            Tensor(shape, dtype, initializer=InitCoords2DArange(h_start,h_stop,w_start,w_stop )).np()

            print('pass')

def concat_test():
    for shape_len in range(2, 5):
        for dtype in HType.get_np_scalar_types():
            shape = (np.random.randint( 8, size=(shape_len,) )+1).tolist()
            axis = np.random.randint(shape_len)
            count = np.random.randint(4)+1

            shapes = tuple( tuple( dim if i != axis else np.random.randint(8)+1
                                    for i,dim in enumerate(shape) )
                            for shape in ([shape] * count) )

            print(f'concat: {shapes} axis={axis} {np.dtype(dtype).name} ... ', end='', flush=True)

            V_n = [ np.random.randint( 2**8, size=shape ).astype(dtype) for shape in shapes ]
            O_n = np.concatenate(V_n, axis)

            print(f'{O_n.shape} == ', end='', flush=True)

            V_t = [ Tensor.from_value(V_n[i]) for i in range(count) ]
            O_t = op.concat(V_t, axis)

            print(f'{O_t.shape} ... ', end='', flush=True)

            if O_n.shape != O_t.shape:
                raise Exception('shape is not equal')

            if not all ( np.ndarray.flatten( O_t.np() == O_n ) ):
                raise Exception(f'data is not equal')

            print('pass')

def matmul_test():
    for _ in range(100):
        for dtype in [np.float32]:
            BATCH = np.random.randint(8)+1
            M = np.random.randint(8)+1
            N = np.random.randint(32768)+1
            K = np.random.randint(32768)+1

            while K*N > ( 8000000 // BATCH ):
                K = max(1, K // 2)
                N = max(1, N // 2)

            if np.random.randint(2) == 0:
                size = [2,4,8,16][np.random.randint(4)]
                M = max(1, M // size) * size
                N = max(1, N // size) * size
                K = max(1, K // size) * size

            if BATCH == 1:
                A_shape = (M, K)
                B_shape = (K, N)
            else:
                A_shape = (BATCH, M, K)
                B_shape = (BATCH, K, N)

            print(f'matmul: {A_shape} {B_shape} {np.dtype(dtype).name} ... ', end='', flush=True)

            A_n = np.random.randint( 2**4, size=A_shape ).astype(dtype)
            B_n = np.random.randint( 2**4, size=B_shape ).astype(dtype)

            O_n = np.matmul(A_n, B_n)

            print(f'{O_n.shape} == ', end='', flush=True)

            A_t = Tensor.from_value(A_n)
            B_t = Tensor.from_value(B_n)
            O_t = op.matmul(A_t, B_t)
            print(f'{O_t.shape} ... ', end='', flush=True)

            if O_n.shape != O_t.shape:
                raise Exception('shape is not equal')
            if not _all_close (O_t.np(), O_n):
                raise Exception(f'data is not equal')

            print('pass')

def slice_test():
    for iteration in [0,1]:
      for shape_len in range(5,1,-1):
          for dtype in HType.get_np_scalar_types():
            while True:
                shape = np.random.randint( 1, 8, size=(shape_len,) )

                if iteration == 0:
                    slices = [ slice(None,None,None), ] * shape_len
                    axis = np.random.randint(shape_len)
                    shape[axis] = 1
                    slices[axis] = 0
                else:
                    slices = []
                    for i in range (shape_len):
                        axis_size = shape[i]
                        b = np.random.randint(axis_size)
                        e = np.random.randint(axis_size)
                        if b == e:
                            slices.append(b)
                        else:
                            if b < e:
                                s = 1
                                if b == 0:
                                    b = None
                                if e == axis_size-1:
                                    e = None
                            else:
                                s = -1
                                if b == axis_size-1:
                                    b = None
                                if e == 0:
                                    e = None
                            slices.append ( slice(b,e,s) )

                    if np.random.randint(2) == 0:
                        axis = np.random.randint(shape_len)
                        slices[axis] = Ellipsis

                shape = tuple(shape)
                slices = tuple(slices)

                print(f'slice: {shape} {np.dtype(dtype).name} {slices} ... ', end='', flush=True)

                val_n = np.random.randint( 2**8, size=shape ).astype(dtype)

                sliced_n = val_n[slices]

                print(f'{sliced_n.shape} ... ', end='', flush=True)

                sliced_t = Tensor.from_value(val_n)[slices]

                print(f'{sliced_t.shape} ... ', end='', flush=True)

                if 0 in sliced_n.shape:
                    # some cases like 0:1:-1 will produce zero shape and invalid array on numpy
                    # but nn.slice has no such behaviour, thus we have to generate new slice again
                    print('pass (bad case)')
                    continue

                if np.prod(sliced_n.shape) != sliced_t.shape.size:
                    raise Exception(f'shape is not equal')

                if not _all_close(sliced_t.np(), sliced_n):
                    raise Exception(f'data is not equal')

                print('pass')
                break


def transpose_test():
    for dtype in HType.get_np_scalar_types():
        for shape_len in range(2, 5):
            shape = np.random.randint( 8, size=(shape_len,) )+1
            axes_order = np.array([*range(shape_len)])
            np.random.shuffle(axes_order)

            print(f'transpose: {shape} {axes_order} ... ', end='', flush=True)

            val_n = np.random.randint( 2**8, size=shape ).astype(dtype)
            transposed_n = np.transpose(val_n, axes_order)

            print(f'{transposed_n.shape} ... ', end='', flush=True)

            val_t = Tensor.from_value(val_n)
            transposed_t = op.transpose (val_t, axes_order )

            print(f'{transposed_t.shape} ... ', end='', flush=True)

            if transposed_n.shape != transposed_t.shape:
                raise Exception('shape is not equal')
            if not all ( np.ndarray.flatten( transposed_t.np() == transposed_n ) ):
                raise Exception(f'data is not equal {shape} {axes_order}')

            print('pass')


def any_wise_op_test():
    for op_type in ['square', '+', '-', '*', '/', 'min', 'max']:
        for dtype in HType.get_np_scalar_types():
          if dtype != np.bool_:

            shape_gen = range(1, 5)
            for shape_len in shape_gen:
                a_shape = tuple(np.random.randint( 8, size=(shape_len,) )+1)

                if np.random.randint(2) == 0:
                    b_shape = tuple(a_shape[np.random.randint(len(a_shape)):])
                    b_shape = (1,) if len(b_shape) == 0 else b_shape
                else:
                    b_shape = list(a_shape)
                    b_shape[ np.random.randint(len(b_shape)) ] = 1
                    b_shape = tuple(b_shape)

                shapes = [a_shape, b_shape]
                if np.random.randint(2) == 0:
                    shapes = shapes[::-1]
                a_shape, b_shape = shapes

                print(f'any_wise: {a_shape} {str(op_type)} {b_shape}:{str(np.dtype(dtype).name)} ...', end='', flush=True)

                a_n = np.random.randint( 1, 2**8, size=a_shape ).astype(dtype)
                b_n = np.random.randint( 1, 2**8, size=b_shape ).astype(dtype)
                a_t = Tensor.from_value(a_n)
                b_t = Tensor.from_value(b_n)

                if op_type == '+':
                    r_t = a_t + b_t
                elif op_type == '-':
                    r_t = a_t - b_t
                elif op_type == '*':
                    r_t = a_t * b_t
                elif op_type == '/':
                    r_t = a_t / b_t
                elif op_type == 'min':
                    r_t = op.min_(a_t, b_t)
                elif op_type == 'max':
                    r_t = op.max_(a_t, b_t)
                elif op_type == 'square':
                    r_t = op.square(a_t)

                if op_type in ['+','-','*','/']:
                    r_n = eval(f'a_n {op_type} b_n')
                    r_n = r_n.astype(dtype)
                elif op_type == 'min':
                    r_n = np.minimum(a_n, b_n)
                elif op_type == 'max':
                    r_n = np.maximum(a_n, b_n)
                elif op_type == 'square':
                    r_n = np.square(a_n)

                if r_n.shape != r_t.shape:
                    raise Exception(f'shapes are not equal')

                if not _all_close(r_t.np(), r_n):
                    raise Exception(f'data is not equal')

                print('pass')


