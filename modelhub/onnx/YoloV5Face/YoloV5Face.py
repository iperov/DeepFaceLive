from pathlib import Path
from typing import List
import numpy as np
from xlib import math as lib_math
from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)


class YoloV5Face:
    """
    YoloV5Face face detection model.

    arguments

     device_info    ORTDeviceInfo

        use YoloV5Face.get_available_devices()
        to determine a list of avaliable devices accepted by model

    raises
     Exception
    """

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        return get_available_devices_info()

    def __init__(self, device_info : ORTDeviceInfo ):
        if device_info not in YoloV5Face.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for YoloV5Face')

        path = Path(__file__).parent / 'YoloV5Face.onnx'
        self._sess = sess = InferenceSession_with_device(str(path), device_info)
        self._input_name = sess.get_inputs()[0].name

    def extract(self, img, threshold : float = 0.3, fixed_window=0, min_face_size=8, augment=False):
        """
        arguments

         img    np.ndarray      ndim 2,3,4

         fixed_window(0)    int  size
                                 0 mean don't use
                                 fit image in fixed window
                                 downscale if bigger than window
                                 pad if smaller than window
                                 increases performance, but decreases accuracy

         min_face_size(8)

         augment(False)     bool    augment image to increase accuracy
                                    decreases performance

        returns a list of [l,t,r,b] for every batch dimension of img
        """

        ip = ImageProcessor(img)
        _,H,W,_ = ip.get_dims()
        if H > 2048 or W > 2048:
            fixed_window = 2048

        if fixed_window != 0:
            fixed_window = max(32, max(1, fixed_window // 32) * 32 )
            img_scale = ip.fit_in(fixed_window, fixed_window, pad_to_target=True, allow_upscale=False)
        else:
            ip.pad_to_next_divisor(64, 64)
            img_scale = 1.0

        ip.ch(3).to_ufloat32()

        _,H,W,_ = ip.get_dims()
        
        preds = self._get_preds(ip.get_image('NCHW'))

        if augment:
            rl_preds = self._get_preds( ip.flip_horizontal().get_image('NCHW') )
            rl_preds[:,:,0] = W-rl_preds[:,:,0]
            preds = np.concatenate([preds, rl_preds],1)

        faces_per_batch = []
        for pred in preds:
            pred = pred[pred[...,4] >= threshold]

            x,y,w,h,score = pred.T

            l, t, r, b = x-w/2, y-h/2, x+w/2, y+h/2
            keep = lib_math.nms(l,t,r,b, score, 0.5)
            l, t, r, b = l[keep], t[keep], r[keep], b[keep]

            faces = []
            for l,t,r,b in np.stack([l, t, r, b], -1):
                if img_scale != 1.0:
                    l,t,r,b = l/img_scale, t/img_scale, r/img_scale, b/img_scale

                if min(r-l,b-t) < min_face_size:
                   continue
                faces.append( (l,t,r,b) )

            faces_per_batch.append(faces)

        return faces_per_batch

    def _get_preds(self, img):
        N,C,H,W = img.shape
        preds = self._sess.run(None, {self._input_name: img})
        # YoloV5Face returns 3x [N,C*16,H,W].
        # C = [cx,cy,w,h,thres, 5*x,y of landmarks, cls_id ]
        # Transpose and cut first 5 channels.
        pred0, pred1, pred2 = [pred.reshape( (N,C,16,pred.shape[-2], pred.shape[-1]) ).transpose(0,1,3,4,2)[...,0:5] for pred in preds]

        pred0 = YoloV5Face.process_pred(pred0, W, H, anchor=[ [4,5],[8,10],[13,16] ]  ).reshape( (N, -1, 5) )
        pred1 = YoloV5Face.process_pred(pred1, W, H, anchor=[ [23,29],[43,55],[73,105] ]  ).reshape( (N, -1, 5) )
        pred2 = YoloV5Face.process_pred(pred2, W, H, anchor=[ [146,217],[231,300],[335,433] ]  ).reshape( (N, -1, 5) )

        return np.concatenate( [pred0, pred1, pred2], 1 )[...,:5]

    @staticmethod
    def process_pred(pred, img_w, img_h, anchor):
        pred_h = pred.shape[-3]
        pred_w = pred.shape[-2]
        anchor = np.float32(anchor)[None,:,None,None,:]

        _xv, _yv,  = np.meshgrid(np.arange(pred_w), np.arange(pred_h), )
        grid = np.stack((_xv, _yv), 2).reshape((1, 1, pred_h, pred_w, 2)).astype(np.float32)

        stride = (img_w // pred_w, img_h // pred_h)

        pred[..., [0,1,2,3,4] ] = YoloV5Face._np_sigmoid(pred[..., [0,1,2,3,4] ])

        pred[..., 0:2] = (pred[..., 0:2]*2 - 0.5 + grid) * stride
        pred[..., 2:4] = (pred[..., 2:4]*2)**2 * anchor
        return pred

    @staticmethod
    def _np_sigmoid(x : np.ndarray):
        """
        sigmoid with safe check of overflow
        """
        x = -x
        c = x > np.log( np.finfo(x.dtype).max )
        x[c] = 0.0
        result = 1 / (1+np.exp(x))
        result[c] = 0.0
        return result
