from pathlib import Path
from typing import List

import numpy as np
from xlib.file import SplittedFile
from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)

import cv2 
import onnx
from onnx import numpy_helper

class InsightFaceSwap:
    """

    arguments

     device_info    ORTDeviceInfo

        use LIA.get_available_devices()
        to determine a list of avaliable devices accepted by model

    raises
     Exception
    """

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        return get_available_devices_info()

    def __init__(self, device_info : ORTDeviceInfo):
        if device_info not in InsightFaceSwap.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for InsightFaceSwap')

        inswapper_path = Path(__file__).parent / 'inswapper_128.onnx'
        SplittedFile.merge(inswapper_path, delete_parts=False)
        if not inswapper_path.exists():
            raise FileNotFoundError(f'{inswapper_path} not found')
        
        w600k_path = Path(__file__).parent / 'w600k_r50.onnx'
        SplittedFile.merge(w600k_path, delete_parts=False)
        if not w600k_path.exists():
            raise FileNotFoundError(f'{w600k_path} not found')
        
        self._sess_swap = InferenceSession_with_device(str(inswapper_path), device_info)
        self._sess_rec =  InferenceSession_with_device(str(w600k_path), device_info)
        
        swap_onnx_model = onnx.load(str(inswapper_path))
        self._emap = numpy_helper.to_array(swap_onnx_model.graph.initializer[-1])
    
    def get_input_size(self):
        """
        returns optimal Width/Height for input images, thus you can resize source image to avoid extra load
        """
        return 128
        
    def get_face_vector_input_size(self):
        return 112
        
    
    def get_face_vector(self, img : np.ndarray) -> np.ndarray:
        ip = ImageProcessor(img)
        ip.fit_in(TW=112, TH=112, pad_to_target=True, allow_upscale=True)
        
        img = ip.ch(3).to_ufloat32().get_image('NCHW')
        
        latent = self._sess_rec.run([self._sess_rec.get_outputs()[0].name], {self._sess_rec.get_inputs()[0].name: img,})[0]
        latent = np.dot(latent.reshape(1, -1,), self._emap)
        latent /= np.linalg.norm(latent)
        return latent

    def generate(self, img : np.ndarray, face_vector : np.ndarray):
        """
        arguments

         img                  np.ndarray      HW HWC 1HWC   uint8/float32
         
         face_vector          np.ndarray
        """  
        ip_target = ImageProcessor(img)

        dtype = ip_target.get_dtype()
        _,H,W,_ = ip_target.get_dims()

        out = self._sess_swap.run(['output'], {'target' : ip_target.resize( (128, 128) ).ch(3).to_ufloat32().get_image('NCHW'), 
                                               'source' : face_vector}
                                               )[0].transpose(0,2,3,1)[0]

        out = ImageProcessor(out).to_dtype(dtype).resize((W,H)).get_image('HWC')

        return out

