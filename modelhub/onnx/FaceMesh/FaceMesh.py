from pathlib import Path
from typing import List

from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)


class FaceMesh:
    """
    Google FaceMesh detection model.
    
    arguments

     device_info    ORTDeviceInfo

        use FaceMesh.get_available_devices()
        to determine a list of avaliable devices accepted by model

    raises
     Exception
    """

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        return get_available_devices_info()

    def __init__(self, device_info : ORTDeviceInfo):
        if device_info not in FaceMesh.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for FaceMesh')

        path = Path(__file__).parent / 'FaceMesh.onnx'
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

        returns (N,468,3)
        """
        ip = ImageProcessor(img)
        N,H,W,_ = ip.get_dims()

        h_scale = H / self._input_height
        w_scale = W / self._input_width

        feed_img = ip.resize( (self._input_width, self._input_height) ).to_ufloat32().ch(3).get_image('NHWC')

        lmrks = self._sess.run(None, {self._input_name: feed_img})[0]
        lmrks = lmrks.reshape( (N,468,3))
        lmrks *= (w_scale, h_scale, 1)

        return lmrks
