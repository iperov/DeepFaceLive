from pathlib import Path
from typing import List

import cv2
import numpy as np
from xlib.file import SplittedFile
from xlib.image import ImageProcessor
from xlib.onnxruntime import (InferenceSession_with_device, ORTDeviceInfo,
                              get_available_devices_info)


class TPSMM:
    """
    [CVPR2022] Thin-Plate Spline Motion Model for Image Animation
    https://github.com/yoyo-nb/Thin-Plate-Spline-Motion-Model

    arguments

     device_info    ORTDeviceInfo

        use TPSMM.get_available_devices()
        to determine a list of avaliable devices accepted by model

    raises
     Exception
    """

    @staticmethod
    def get_available_devices() -> List[ORTDeviceInfo]:
        return get_available_devices_info()

    def __init__(self, device_info : ORTDeviceInfo):
        if device_info not in TPSMM.get_available_devices():
            raise Exception(f'device_info {device_info} is not in available devices for TPSMM')
        
        generator_path = Path(__file__).parent / 'generator.onnx'
        SplittedFile.merge(generator_path, delete_parts=False)
        if not generator_path.exists():
            raise FileNotFoundError(f'{generator_path} not found')
            
        kp_detector_path = Path(__file__).parent / 'kp_detector.onnx'
        if not kp_detector_path.exists():
            raise FileNotFoundError(f'{kp_detector_path} not found')

        self._generator = InferenceSession_with_device(str(generator_path), device_info)
        self._kp_detector = InferenceSession_with_device(str(kp_detector_path), device_info)


    def get_input_size(self):
        """
        returns optimal (Width,Height) for input images, thus you can resize source image to avoid extra load
        """
        return (256,256)

    def extract_kp(self, img : np.ndarray):
        """
        Extract keypoints from image

        arguments

         img    np.ndarray      HW HWC 1HWC   uint8/float32
        """
        feed_img = ImageProcessor(img).resize(self.get_input_size()).swap_ch().to_ufloat32().ch(3).get_image('NCHW')
        return self._kp_detector.run(None, {'in': feed_img})[0]

    def generate(self, img_source : np.ndarray, kp_source : np.ndarray, kp_driver : np.ndarray, kp_driver_ref : np.ndarray = None, relative_power : float = 1.0):
        """

        arguments

         img_source    np.ndarray      HW HWC 1HWC   uint8/float32
         
         kp_driver_ref      specify to work in kp relative mode
        """
        if kp_driver_ref is not None:
            kp_driver = self.calc_relative_kp(kp_source=kp_source, kp_driver=kp_driver, kp_driver_ref=kp_driver_ref, power=relative_power)

        theta, control_points, control_params = self.create_transformations_params(kp_source, kp_driver)

        ip = ImageProcessor(img_source)
        dtype = ip.get_dtype()
        _,H,W,_ = ip.get_dims()

        feed_img = ip.resize(self.get_input_size()).to_ufloat32().ch(3).get_image('NCHW')

        out = self._generator.run(None, {'in': feed_img,
                                         'theta' : theta,
                                         'control_points' : control_points,
                                         'control_params' : control_params,
                                         'kp_driver' : kp_driver,
                                         'kp_source' : kp_source,
                                         })[0].transpose(0,2,3,1)[0]

        out = ImageProcessor(out).resize( (W,H)).to_dtype(dtype).get_image('HWC')
        return out

    def calc_relative_kp(self, kp_source, kp_driver, kp_driver_ref, power = 1.0):
        source_area  = np.array([ cv2.contourArea(cv2.convexHull(pts)) for pts in kp_source ], dtype=kp_source.dtype)
        driving_area = np.array([ cv2.contourArea(cv2.convexHull(pts)) for pts in kp_driver_ref ], dtype=kp_driver_ref.dtype)
        movement_scale = np.sqrt(source_area) / np.sqrt(driving_area)
        return kp_source + (kp_driver - kp_driver_ref) * movement_scale[:,None,None] * power

    def create_transformations_params(self, kp_source, kp_driver):
        kp_num=10
        kp_sub_num=5

        kp_d = kp_driver.reshape(-1, kp_num, kp_sub_num, 2)
        kp_s = kp_source.reshape(-1, kp_num, kp_sub_num, 2)


        K = np.linalg.norm(kp_d[:,:,:,None]-kp_d[:,:,None,:], ord=2, axis=4) ** 2
        K = K * np.log(K+1e-9)

        kp_1d = np.concatenate([kp_d, np.ones(kp_d.shape[:-1], dtype=kp_d.dtype)[...,None] ], -1)

        P = np.concatenate([kp_1d, np.zeros(kp_d.shape[:2] + (3, 3), dtype=kp_d.dtype)], 2)
        L = np.concatenate([K,kp_1d.transpose(0,1,3,2)],2)
        L = np.concatenate([L,P],3)

        Y = np.concatenate([kp_s, np.zeros(kp_d.shape[:2] + (3, 2), dtype=kp_d.dtype)], 2)

        one = np.broadcast_to( np.eye(Y.shape[2], dtype=kp_d.dtype), L.shape)*0.01

        L = L + one

        param = np.matmul(np.linalg.inv(L),Y)

        theta = param[:,:,kp_sub_num:,:].transpose(0,1,3,2)
        control_points = kp_d
        control_params = param[:,:,:kp_sub_num,:]
        return theta, control_points, control_params
