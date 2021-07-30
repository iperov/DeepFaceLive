from pathlib import Path
from typing import List

import numpy as np
from xlib import math as lib_math
from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)

from xlib.file import SplittedFile

class S3FD:

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        return get_available_devices_info()

    def __init__(self, device_info : ORTDeviceInfo ):
        if device_info not in S3FD.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for S3FD')

        path = Path(__file__).parent / 'S3FD.onnx'
        SplittedFile.merge(path, delete_parts=False)
        
        self._sess = sess = InferenceSession_with_device(str(path), device_info)
        self._input_name = sess.get_inputs()[0].name


    def extract(self, img : np.ndarray, threshold=0.95, fixed_window=0, min_face_size=40):
        """

            img     HW,HWC,NHWC     [0..255]
        """
        ip = ImageProcessor(img)

        if fixed_window != 0:
            fixed_window = max(64, max(1, fixed_window // 32) * 32 )
            img_scale = ip.fit_in(fixed_window, fixed_window, pad_to_target=True, allow_upscale=False)
        else:
            ip.pad_to_next_divisor(64, 64)
            img_scale = 1.0

        img = ip.ch(3).to_uint8().as_float32().apply( lambda img: img - [104,117,123]).get_image('NCHW')

        batches_bbox = self._sess.run(None, {self._input_name: img})

        faces_per_batch = []
        for batch in range(img.shape[0]):
            bbox = self.refine( [ x[batch] for x in batches_bbox ], threshold )

            faces = []
            for l,t,r,b,c in bbox:
                if img_scale != 1.0:
                    l,t,r,b = l/img_scale, t/img_scale, r/img_scale, b/img_scale

                bt = b-t
                if min(r-l,bt) < min_face_size:
                    continue
                b += bt*0.1

                faces.append ( (l,t,r,b) )

            faces_per_batch.append(faces)

        return faces_per_batch


    def refine(self, olist, threshold):
        bboxlist = []
        variances = [0.1, 0.2]
        for i in range(len(olist) // 2):
            ocls, oreg = olist[i * 2], olist[i * 2 + 1]

            stride = 2**(i + 2)    # 4,8,16,32,64,128
            for hindex, windex in [*zip(*np.where(ocls[1, :, :] > threshold))]:
                axc, ayc = stride / 2 + windex * stride, stride / 2 + hindex * stride
                score = ocls[1, hindex, windex]
                loc = np.ascontiguousarray(oreg[:, hindex, windex]).reshape((1, 4))
                priors = np.array([[axc, ayc, stride * 4, stride * 4]])
                bbox = np.concatenate((priors[:, :2] + loc[:, :2] * variances[0] * priors[:, 2:],
                                       priors[:, 2:] * np.exp(loc[:, 2:] * variances[1])), 1)
                bbox[:, :2] -= bbox[:, 2:] / 2
                bbox[:, 2:] += bbox[:, :2]
                x1, y1, x2, y2 = bbox[0]
                bboxlist.append([x1, y1, x2, y2, score])

        if len(bboxlist) != 0:
            bboxlist = np.array(bboxlist)
            bboxlist = bboxlist[ lib_math.nms(bboxlist[:,0], bboxlist[:,1], bboxlist[:,2], bboxlist[:,3], bboxlist[:,4], 0.3), : ]
            bboxlist = [x for x in bboxlist if x[-1] >= 0.5]

        return bboxlist
