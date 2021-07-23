from pathlib import Path
from typing import List

import numpy as np
from xlib import math as lib_math
from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)


class CenterFace:
    """
    CenterFace face detection model.

    arguments

     device_info    ORTDeviceInfo

        use CenterFace.get_available_devices()
        to determine a list of avaliable devices accepted by model

    raises
     Exception
    """

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        # CenterFace ONNX model does not work correctly on CPU
        # but it is much faster than Pytorch version
        return get_available_devices_info(include_cpu=False)

    def __init__(self, device_info : ORTDeviceInfo ):

        if device_info not in CenterFace.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for CenterFace')

        path = Path(__file__).parent / 'CenterFace.onnx'
        self._sess = sess = InferenceSession_with_device(str(path), device_info)
        self._input_name = sess.get_inputs()[0].name

    def extract(self, img, threshold : float = 0.5, fixed_window=0, min_face_size=40):
        """
        arguments

         img    np.ndarray      ndim 2,3,4

         fixed_window(0)    int  size
                                 0 mean don't use
                                 fit image in fixed window
                                 downscale if bigger than window
                                 pad if smaller than window
                                 increases performance, but decreases accuracy

        returns a list of [l,t,r,b] for every batch dimension of img
        """

        ip = ImageProcessor(img)
        N,H,W,_ = ip.get_dims()

        if fixed_window != 0:
            fixed_window = max(64, max(1, fixed_window // 32) * 32 )
            img_scale = ip.fit_in(fixed_window, fixed_window, pad_to_target=True, allow_upscale=False)
        else:
            ip.pad_to_next_divisor(64, 64)
            img_scale = 1.0

        img = ip.ch(3).swap_ch().to_uint8().as_float32().get_image('NCHW')

        heatmaps, scales, offsets = self._sess.run(None, {self._input_name: img})
        faces_per_batch = []

        for heatmap, offset, scale in zip(heatmaps, offsets, scales):
            faces = []
            for face in self.refine(heatmap, offset, scale, H, W, threshold):
                l,t,r,b,c = face

                if img_scale != 1.0:
                    l,t,r,b = l/img_scale, t/img_scale, r/img_scale, b/img_scale

                bt = b-t
                if min(r-l,bt) < min_face_size:
                   continue
                b += bt*0.1

                faces.append( (l,t,r,b) )

            faces_per_batch.append(faces)

        return faces_per_batch

    def refine(self, heatmap, offset, scale, h, w, threshold):
        heatmap = heatmap[0]
        scale0, scale1 = scale[0, :, :], scale[1, :, :]
        offset0, offset1 = offset[0, :, :], offset[1, :, :]
        c0, c1 = np.where(heatmap > threshold)
        bboxlist = []
        if len(c0) > 0:
            for i in range(len(c0)):
                s0, s1 = np.exp(scale0[c0[i], c1[i]]) * 4, np.exp(scale1[c0[i], c1[i]]) * 4
                o0, o1 = offset0[c0[i], c1[i]], offset1[c0[i], c1[i]]
                s = heatmap[c0[i], c1[i]]
                x1, y1 = max(0, (c1[i] + o1 + 0.5) * 4 - s1 / 2), max(0, (c0[i] + o0 + 0.5) * 4 - s0 / 2)
                x1, y1 = min(x1, w), min(y1, h)
                bboxlist.append([x1, y1, min(x1 + s1, w), min(y1 + s0, h), s])

            bboxlist = np.array(bboxlist, dtype=np.float32)

            bboxlist = bboxlist[ lib_math.nms(bboxlist[:,0], bboxlist[:,1], bboxlist[:,2], bboxlist[:,3], bboxlist[:,4], 0.3), : ]
            bboxlist = [x for x in bboxlist if x[-1] >= 0.5]

        return bboxlist
