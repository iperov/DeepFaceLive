from enum import IntEnum
from typing import Tuple, Union

import cupy as cp
import cupyx.scipy.ndimage
import cv2
import numexpr as ne
import numpy as np
import scipy
import scipy.ndimage


class ImageProcessor:
    """
    Generic image processor for numpy or cupy images

    arguments

     img    np.ndarray|
            cp.ndarray
                        HW   (2 ndim)
                        HWC  (3 ndim)
                        NHWC (4 ndim)

    for cupy you should set device before using ImageProcessor
    """
    def __init__(self, img : Union[np.ndarray,cp.ndarray], copy=False):
        self._xp = xp = cp.get_array_module(img)

        if copy and xp == np:
            img = img.copy()

        self._sp = cupyx.scipy if xp == cp else scipy

        ndim = img.ndim
        if ndim not in [2,3,4]:
            raise ValueError(f'img.ndim must be 2,3,4, not {ndim}.')

        # Make internal image as NHWC
        if ndim == 2:
            N, (H,W), C = 0, img.shape, 0
            img = img[None,:,:,None]
        elif ndim == 3:
            N, (H,W,C) = 0, img.shape
            img = img[None,...]
        else:
            N,H,W,C = img.shape

        self._img : np.ndarray = img

    def copy(self) -> 'ImageProcessor':
        """
        """
        ip = ImageProcessor.__new__(ImageProcessor)
        ip._img = self._img
        ip._xp = self._xp
        ip._sp = self._sp
        return ip

    def get_dims(self) -> Tuple[int,int,int,int]:
        """
        returns dimensions of current working image

        returns N,H,W,C (ints) , each >= 1
        """
        return self._img.shape

    def get_dtype(self):
        return self._img.dtype

    def adjust_gamma(self, red : float, green : float, blue : float) -> 'ImageProcessor':
        dtype = self.get_dtype()
        self.to_ufloat32()

        xp, img = self._xp , self._img,

        xp.power(img, xp.array([1.0 / blue, 1.0 / green, 1.0 / red], xp.float32), out=img)
        xp.clip(img, 0, 1.0, out=img)

        self._img = img

        self.to_dtype(dtype)

        return self


    def apply(self, func) -> 'ImageProcessor':
        """
        apply your own function on internal image

        image has NHWC format. Do not change format, but dims can be changed.

         func   callable  (img) -> img

        example:

         .apply( lambda img: img-[102,127,63] )
        """
        img = self._img
        dtype = img.dtype
        new_img = func(self._img).astype(dtype)
        if new_img.ndim != 4:
            raise Exception('func used in ImageProcessor.apply changed format of image')
        self._img = new_img
        return self

    def fit_in (self, TW = None, TH = None, pad_to_target : bool = False, allow_upscale : bool = False, interpolation : 'ImageProcessor.Interpolation' = None) -> float:
        """
        fit image in w,h keeping aspect ratio


            TW,TH           int/None     target width,height


            pad_to_target   bool    pad remain area with zeros

            allow_upscale   bool    if image smaller than TW,TH it will be upscaled

            interpolation   ImageProcessor.Interpolation. value

        returns scale float value
        """
        #if interpolation is None:
        #    interpolation = ImageProcessor.Interpolation.LINEAR
        xp, sp = self._xp, self._sp
        img = self._img
        N,H,W,C = img.shape

        if TW is not None and TH is None:
            scale = TW / W
        elif TW is None and TH is not None:
            scale = TH / H
        elif TW is not None and TH is not None:
            SW = W / TW
            SH = H / TH
            scale = 1.0
            if SW > 1.0 or SH > 1.0 or (SW < 1.0 and SH < 1.0):
                scale /= max(SW, SH)
        else:
            raise ValueError('TW or TH should be specified')

        if not allow_upscale and scale > 1.0:
            scale = 1.0

        if scale != 1.0:
            img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

            if self._xp == cp:
                img = sp.ndimage.zoom(img, (scale, scale, 1.0), order=1)
            else:
                img = cv2.resize (img, ( int(W*scale), int(H*scale) ), interpolation=ImageProcessor.Interpolation.LINEAR)

            H,W,_ = img.shape
            img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if pad_to_target:
            w_pad = (TW-W) if TW is not None else 0
            h_pad = (TH-H) if TH is not None else 0
            if w_pad != 0 or h_pad != 0:
                img = xp.pad(img, ( (0,0), (0,h_pad), (0,w_pad), (0,0) ))
        self._img = img

        return scale

    def clip(self, min, max) -> 'ImageProcessor':
        xp = self._xp
        xp.clip(self._img, min, max, out=self._img)
        return self

    def clip2(self, low_check, low_val, high_check, high_val) -> 'ImageProcessor':
        img = self._img
        l, h = img < low_check, img > high_check
        img[l] = low_val
        img[h] = high_val
        return self

    def degrade_resize(self, power : float, interpolation : 'ImageProcessor.Interpolation' = None) -> 'ImageProcessor':
        """

         power  float   0 .. 1.0
        """
        power = min(1, max(0, power))
        if power == 0:
            return self

        if interpolation is None:
            interpolation = ImageProcessor.Interpolation.LINEAR

        xp, sp, img = self._xp, self._sp, self._img

        N,H,W,C = img.shape
        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        if xp == cp:
            W_lr = max(4, round(W*(1.0-power)))
            H_lr = max(4, round(H*(1.0-power)))
            img = sp.ndimage.zoom(img, (H_lr/H, W_lr/W, 1), order=_scipy_order[interpolation])
            img = sp.ndimage.zoom(img, (H/img.shape[0], W/img.shape[1], 1), order=_scipy_order[interpolation])
        else:
            W_lr = max(4, int(W*(1.0-power)))
            H_lr = max(4, int(H*(1.0-power)))
            img = cv2.resize (img, (W_lr,H_lr), interpolation=_cv_inter[interpolation])
            img = cv2.resize (img, (W,H)      , interpolation=_cv_inter[interpolation])

        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        self._img = img
        return self


    def median_blur(self, size : int, power : float) -> 'ImageProcessor':
        """
         size   int     median kernel size

         power  float   0 .. 1.0
        """
        power = min(1, max(0, power))
        if power == 0:
            return self

        dtype = self.get_dtype()
        self.to_ufloat32()

        xp, sp, img = self._xp, self._sp, self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        if xp == cp:
            img_blur = sp.ndimage.median_filter(img, size=(size,size,1) )
            img = img*(1.0-power) + img_blur*power
        else:
            img_blur = cv2.medianBlur(img, size)
            img = ne.evaluate('img*(1.0-power) + img_blur*power')

        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )
        self._img = img

        self.to_dtype(dtype)
        return self

    def erode_blur(self, erode : int, blur : int, fade_to_border : bool = False) -> 'ImageProcessor':
        """
        apply erode and blur to the image

         erode  int     != 0
         blur   int     > 0
         fade_to_border(False)  clip the image in order
                                to fade smoothly to the border with specified blur amount
        """
        xp, sp = self._xp, self._sp

        erode, blur = int(erode), int(blur)

        img = self._img
        dtype = img.dtype
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )
        img = xp.pad (img, ( (H,H), (W,W), (0,0) ) )

        if erode > 0:
            el = xp.asarray(cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
            iterations = max(1,erode//2)
            if self._xp == cp:
                img = sp.ndimage.binary_erosion(img, el[...,None], iterations = iterations, brute_force=True ).astype(dtype)
            else:
                img = cv2.erode(img, el, iterations = iterations )

        elif erode < 0:
            el = xp.asarray(cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
            iterations = max(1,-erode//2)
            if self._xp == cp:
                img = sp.ndimage.binary_dilation(img, el[...,None], iterations = iterations, brute_force=True).astype(dtype)
            else:
                img = cv2.dilate(img, el, iterations = iterations )

        if fade_to_border:
            h_clip_size = H + blur // 2
            w_clip_size = W + blur // 2
            img[:h_clip_size,:] = 0
            img[-h_clip_size:,:] = 0
            img[:,:w_clip_size] = 0
            img[:,-w_clip_size:] = 0

        if blur > 0:
            sigma = blur * 0.125 * 2
            if self._xp == cp:
                img = sp.ndimage.gaussian_filter(img, (sigma, sigma,0), mode='constant')
            else:
                img = cv2.GaussianBlur(img, (0, 0), sigma)

        #if img.ndim == 2:
        #    img = img[...,None]
        img = img[H:-H,W:-W]
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        self._img = img
        return self

    def rotate90(self) -> 'ImageProcessor':
        self._img = self._xp.rot90(self._img, k=1, axes=(1,2) )
        return self

    def rotate180(self) -> 'ImageProcessor':
        self._img = self._xp.rot90(self._img, k=2, axes=(1,2) )
        return self

    def rotate270(self) -> 'ImageProcessor':
        self._img = self._xp.rot90(self._img, k=3, axes=(1,2) )
        return self

    def flip_horizontal(self) -> 'ImageProcessor':
        """

        """
        self._img = self._img[:,:,::-1,:]
        return self

    def flip_vertical(self) -> 'ImageProcessor':
        """

        """
        self._img = self._img[:,::-1,:,:]
        return self

    def pad(self, t_h, b_h, l_w, r_w) -> 'ImageProcessor':
        """

        """
        xp = self._xp
        img = self._img
        img = xp.pad(img, ( (0,0), (t_h,b_h), (l_w,r_w), (0,0) ))

        self._img = img
        return self

    def pad_to_next_divisor(self, dw=None, dh=None) -> 'ImageProcessor':
        """
        pad image to next divisor of width/height

         dw,dh  int
        """
        xp = self._xp
        img = self._img
        _,H,W,_ = img.shape

        w_pad = 0
        if dw is not None:
            w_pad = W % dw
            if w_pad != 0:
                w_pad = dw - w_pad

        h_pad = 0
        if dh is not None:
            h_pad = H % dh
            if h_pad != 0:
                h_pad = dh - h_pad

        if w_pad != 0 or h_pad != 0:
            img = xp.pad(img, ( (0,0), (0,h_pad), (0,w_pad), (0,0) ))

        self._img = img
        return self

    def sharpen(self, factor : float, kernel_size=3) -> 'ImageProcessor':
        xp = self._xp
        img = self._img

        N,H,W,C = img.shape
        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        if xp == cp:
            raise
        else:
            blur = cv2.GaussianBlur(img, (kernel_size, kernel_size) , 0)
            img = cv2.addWeighted(img, 1.0 + (0.5 * factor), blur, -(0.5 * factor), 0)

        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        self._img = img
        return self

    def get_image(self, format) -> np.ndarray:
        """
        returns image with desired format

            format    str      examples:
                                NHWC, HWCN, NHW

        if symbol in format does not exist, it will be got from 0 index

        zero dim will be set to 1
        """
        xp = self._xp

        format = format.upper()
        img = self._img

        # First slice missing dims
        N_slice = 0 if 'N' not in format else slice(None)
        H_slice = 0 if 'H' not in format else slice(None)
        W_slice = 0 if 'W' not in format else slice(None)
        C_slice = 0 if 'C' not in format else slice(None)
        img = img[N_slice, H_slice, W_slice, C_slice]

        f = ''
        if 'N' in format: f += 'N'
        if 'H' in format: f += 'H'
        if 'W' in format: f += 'W'
        if 'C' in format: f += 'C'

        if f != format:
            # Transpose to target
            d = { s:i for i,s in enumerate(f) }
            transpose_order = [ d[s] for s in format ]
            img = img.transpose(transpose_order)

        return xp.ascontiguousarray(img)

    def ch(self, TC : int) -> 'ImageProcessor':
        """
        Clips or expands channel dimension to target channels

         TC     int     >= 1
        """
        xp = self._xp
        img = self._img
        N,H,W,C = img.shape

        if TC <= 0:
            raise ValueError(f'channels must be positive value, not {TC}')

        if TC > C:
            # Ch expand
            img = img[...,0:1]  # Clip to single ch first.
            img = xp.repeat (img, TC, -1) # Expand by repeat
        elif TC < C:
            # Ch reduction  clip
            img = img[...,:TC]

        self._img = img
        return self

    def resize(self, size : Tuple, interpolation : 'ImageProcessor.Interpolation' = None, new_ip=False ) -> 'ImageProcessor':
        """
        resize to (W,H)
        """
        xp, sp = self._xp, self._sp

        img = self._img
        N,H,W,C = img.shape

        TW,TH = size
        if W != TW or H != TH:
            if interpolation is None:
                interpolation = ImageProcessor.Interpolation.LINEAR

            img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

            if self._xp == cp:
                img = sp.ndimage.zoom(img, (TW/W, TH/H, 1), order=_scipy_order[interpolation])
            else:
                img = cv2.resize (img, (TW, TH), interpolation=_cv_inter[interpolation])

            img = img.reshape( (TH,TW,N,C) ).transpose( (2,0,1,3) )

            if new_ip:
                return ImageProcessor(img)

            self._img = img

        return self

    def warpAffine(self, mat, out_width, out_height, interpolation : 'ImageProcessor.Interpolation' = None ) -> 'ImageProcessor':
        """
        img    HWC
        """
        xp, sp, img = self._xp, self._sp, self._img
        N,H,W,C = img.shape
        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        if interpolation is None:
            interpolation = ImageProcessor.Interpolation.LINEAR

        if xp == cp:
            # AffineMat inverse
            xp_mat = cp.get_array_module(mat)
            mat = xp_mat.linalg.inv(xp_mat.concatenate( ( mat, xp_mat.array([[0,0,1]], xp_mat.float32)), 0) )[0:2,:]

            mx, my = xp.meshgrid( xp.arange(0, out_width, dtype=xp.float32), xp.arange(0, out_height, dtype=xp.float32) )
            coords = xp.concatenate( (mx[None,...], my[None,...], xp.ones( (1, out_height,out_width), dtype=xp.float32)), 0 )

            mat_coords = xp.matmul (xp.asarray(mat), coords.reshape( (3,-1) ) ).reshape( (2,out_height,out_width))
            img = xp.concatenate([sp.ndimage.map_coordinates( img[...,c], mat_coords[::-1,...], order=_scipy_order[interpolation], mode='opencv' )[...,None] for c in range(N*C) ], -1)

        else:
            img = cv2.warpAffine(img, mat, (out_width, out_height), flags=_cv_inter[interpolation] )

        img = img.reshape( (out_height,out_width,N,C) ).transpose( (2,0,1,3) )
        self._img = img
        return self

    def swap_ch(self) -> 'ImageProcessor':
        """swaps order of channels"""
        self._img = self._img[...,::-1]
        return self

    def as_float32(self) -> 'ImageProcessor':
        """
        change image format to float32
        """
        xp = self._xp
        self._img = self._img.astype(xp.float32)
        return self

    def as_uint8(self) -> 'ImageProcessor':
        """
        change image format to uint8
        """
        xp = self._xp
        self._img = self._img.astype(xp.uint8)
        return self

    def to_dtype(self, dtype) -> 'ImageProcessor':
        xp = self._xp
        if dtype == xp.float32:
            return self.to_ufloat32()
        elif dtype == xp.uint8:
            return self.to_uint8()
        else:
            raise ValueError('unsupported dtype')

    def to_ufloat32(self) -> 'ImageProcessor':
        """
        Convert to uniform float32
        if current image dtype uint8, then image will be divided by / 255.0
        otherwise no operation
        """
        xp = self._xp
        if self._img.dtype == xp.uint8:
            self._img = self._img.astype(xp.float32)
            self._img /= 255.0

        return self

    def to_uint8(self) -> 'ImageProcessor':
        """
        Convert to uint8

        if current image dtype is float32/64, then image will be multiplied by *255
        """
        xp = self._xp
        img = self._img

        if img.dtype in [xp.float32, xp.float64]:
            img *= 255.0
            img[img < 0] = 0
            img[img > 255] = 255

        img = img.astype(xp.uint8, copy=False)
        self._img = img

        return self

    class Interpolation(IntEnum):
        LINEAR = 0
        CUBIC = 1

_cv_inter = { ImageProcessor.Interpolation.LINEAR : cv2.INTER_LINEAR,
              ImageProcessor.Interpolation.CUBIC : cv2.INTER_CUBIC }

_scipy_order = { ImageProcessor.Interpolation.LINEAR : 1,
                 ImageProcessor.Interpolation.CUBIC : 3 }
