from pathlib import Path
from typing import List

from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)

class InsightFace2D106:
    """
    arguments

     device_info    ORTDeviceInfo

        use InsightFace2D106.get_available_devices()
        to determine a list of avaliable devices accepted by model

    raises
     Exception
    """

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        return get_available_devices_info()

    def __init__(self, device_info : ORTDeviceInfo):
        if device_info not in InsightFace2D106.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for InsightFace2D106')

        path = Path(__file__).parent / 'InsightFace2D106.onnx'
        if not path.exists():
            raise FileNotFoundError(f'{path} not found')
            
        self._sess = sess = InferenceSession_with_device(str(path), device_info)
        self._input_name = sess.get_inputs()[0].name
        self._input_width = 192
        self._input_height = 192

    def extract(self, img):
        """
        arguments

         img    np.ndarray      HW,HWC,NHWC uint8/float32

        returns (N,106,2)
        """
        ip = ImageProcessor(img)
        N,H,W,_ = ip.get_dims()

        h_scale = H / self._input_height
        w_scale = W / self._input_width

        feed_img = ip.resize( (self._input_width, self._input_height) ).swap_ch().as_float32().ch(3).get_image('NCHW')

        lmrks = self._sess.run(None, {self._input_name: feed_img})[0]
        lmrks = lmrks.reshape( (N,106,2))
        lmrks /= 2.0
        lmrks += (0.5, 0.5)
        lmrks *= (w_scale, h_scale)
        lmrks *= (W, H)
        
        return lmrks
