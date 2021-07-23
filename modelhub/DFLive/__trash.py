from enum import IntEnum
from pathlib import Path
from typing import List, Union

import cv2
import numpy as np
from xlib.image import ImageProcessor
from xlib.net import ThreadFileDownloader


from xlib import tf

class DFMModelInfo:
    """
    Model for face swapping.
    
    """
    def __init__(self, celeb_type, device):
        celeb_name = str(celeb_type).split('.')[-1]
        model_path = self._model_path = Path(__file__).parent / 'CELEB_MODEL' / f'{celeb_name}.onnx'

        self._dl_error = None
        self._dl = None
        if not model_path.exists():
            self._dl = ThreadFileDownloader(rf'https://github.com/iperov/DeepFaceLive/releases/download/CELEB_MODEL/{celeb_name}.onnx', savepath=model_path)

        self._device = device
        self._sess = None
        
    @staticmethod
    def get_available_devices(celeb_type):
        return tf.get_available_devices_info()
        
    def get_download_error(self) -> Union[str,None]:
        """
        returns download error or None if no error.
        """
        if self._dl_error is not None:
            return 'DFMModelInfo download error: ' + self._dl_error
        return None
        
    def update_download_progress(self) -> float:
        """
        returns [0.0..100.0] where 100.0 mean the model is ready to convert.
        """
        if self._dl_error is not None:
            progress = 0.0 
        elif self._dl is None:
            progress = 100.0
        else:
            err = self._dl_error = self._dl.get_error()
            if err is not None:
                progress = 0.0
            else:
                progress = self._dl.get_progress()
            
        if progress == 100.0 and self._sess is None:
            self._dl = None
            
            model_path = r'D:\DevelopPPP\projects\DeepFaceLive\github_project\xlib\model_hub\tf\TOM_CRUISE.pb'
            self._sess = tf.TFInferenceSession(model_path,
                                 in_tensor_names=['in_face:0', 'morph_value:0'],
                                 out_tensor_names=['out_face_mask:0','out_celeb_face:0','out_celeb_face_mask:0'],
                                 device_info=self._device)
      
            
        return progress
        
    def convert(self, img, morph_factor=0.75):
        """
         img    np.ndarray  HW,HWC,NHWC uint8,float32
         
        returns
        
         img        NHW3  same dtype as img
         celeb_mask NHW1  same dtype as img
         face_mask  NHW1  same dtype as img
        
        convert the face
        if the model is not ready, it will return black images
        """
        
        ip = ImageProcessor(img)
        
        N,H,W,C = ip.get_dims()
        dtype = ip.get_dtype()
        
        progress = self.update_download_progress()
        if progress == 100.0:
        
            img = ip.resize( (224,224) ).ch(3).to_ufloat32().get_image('NHWC')

            #out_face_mask, out_celeb, out_celeb_mask = self._sess.run(None, {self._input_name: img})
            
            out_face_mask, out_celeb, out_celeb_mask = self._sess.run([img, [morph_factor] ])
            
            out_celeb      = ImageProcessor(out_celeb).resize((W,H)).ch(3).to_dtype(dtype).get_image('NHWC')
            out_celeb_mask = ImageProcessor(out_celeb_mask).resize((W,H)).ch(1).to_dtype(dtype).get_image('NHWC')
            out_face_mask  = ImageProcessor(out_face_mask).resize((W,H)).ch(1).to_dtype(dtype).get_image('NHWC')
        else:
            out_celeb = np.zeros( (N,H,W,3), dtype=dtype )
            out_celeb_mask = ImageProcessor(np.full( (N,H,W,1), 255, dtype=np.uint8 )).to_dtype(dtype).get_image('NHWC')
            out_face_mask = ImageProcessor(np.full( (N,H,W,1), 255, dtype=np.uint8 )).to_dtype(dtype).get_image('NHWC')

        return out_celeb, out_celeb_mask, out_face_mask
        
    class CelebType(IntEnum):
        TOM_CRUISE = 0
        VLADIMIR_PUTIN = 1
    
    CelebTypeNames = ['Tom Cruise',
                      'Vladimir Putin']
    
    

