from enum import IntEnum
from typing import Tuple, Union

import cv2
import numexpr as ne
import numpy as np

class ImageProcessor:
    """
    Generic image processor for numpy images

    arguments

     img    np.ndarray  HW   (2 ndim)
                        HWC  (3 ndim)
                        NHWC (4 ndim)

    """
    def __init__(self, img : np.ndarray, copy=False):
        if copy:
            img = img.copy()
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
        ip._img = self._img.copy()
        return ip

    def get_dims(self) -> Tuple[int,int,int,int]:
        """
        returns dimensions of current working image

        returns N,H,W,C (ints) , each >= 1
        """
        return self._img.shape

    def get_dtype(self):
        return self._img.dtype

    def gamma(self, red : float, green : float, blue : float, mask=None) -> 'ImageProcessor':
        dtype = self.get_dtype()
        self.to_ufloat32()
        img = orig_img = self._img

        img = np.power(img, np.array([1.0 / blue, 1.0 / green, 1.0 / red], np.float32) )
        np.clip(img, 0, 1.0, out=img)

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img
        self.to_dtype(dtype)
        return self


    def apply(self, func, mask=None) -> 'ImageProcessor':
        """
        apply your own function on internal image

        image has NHWC format. Do not change format, but dims can be changed.

         func   callable  (img) -> img

        example:

         .apply( lambda img: img-[102,127,63] )
        """
        img = orig_img = self._img
        img = func(img).astype(orig_img.dtype)
        if img.ndim != 4:
            raise Exception('func used in ImageProcessor.apply changed format of image')

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask').astype(orig_img.dtype)

        self._img = img
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
            img = cv2.resize (img, ( int(W*scale), int(H*scale) ), interpolation=ImageProcessor.Interpolation.LINEAR)
            H,W = img.shape[0:2]
            img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if pad_to_target:
            w_pad = (TW-W) if TW is not None else 0
            h_pad = (TH-H) if TH is not None else 0
            if w_pad != 0 or h_pad != 0:
                img = np.pad(img, ( (0,0), (0,h_pad), (0,w_pad), (0,0) ))
        self._img = img

        return scale

    def clip(self, min, max) -> 'ImageProcessor':
        np.clip(self._img, min, max, out=self._img)
        return self

    def clip2(self, low_check, low_val, high_check, high_val) -> 'ImageProcessor':
        img = self._img
        l, h = img < low_check, img > high_check
        img[l] = low_val
        img[h] = high_val
        return self

    def reresize(self, power : float, interpolation : 'ImageProcessor.Interpolation' = None, mask = None) -> 'ImageProcessor':
        """

         power  float   0 .. 1.0
        """
        power = min(1, max(0, power))
        if power == 0:
            return self

        if interpolation is None:
            interpolation = ImageProcessor.Interpolation.LINEAR

        img = orig_img = self._img

        N,H,W,C = img.shape
        W_lr = max(4, int(W*(1.0-power)))
        H_lr = max(4, int(H*(1.0-power)))
        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )
        img = cv2.resize (img, (W_lr,H_lr), interpolation=_cv_inter[interpolation])
        img = cv2.resize (img, (W,H)      , interpolation=_cv_inter[interpolation])
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask').astype(orig_img.dtype)

        self._img = img
        return self

    def box_sharpen(self, size : int, power : float, mask = None) -> 'ImageProcessor':
        """
         size   int     kernel size

         power  float   0 .. 1.0 (or higher)
        """
        power = max(0, power)
        if power == 0:
            return self

        if size % 2 == 0:
            size += 1

        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        kernel = np.zeros( (size, size), dtype=np.float32)
        kernel[ size//2, size//2] = 1.0
        box_filter = np.ones( (size, size), dtype=np.float32) / (size**2)
        kernel = kernel + (kernel - box_filter) * (power)
        img = cv2.filter2D(img, -1, kernel)
        img = np.clip(img, 0, 1, out=img)

        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img
        self.to_dtype(dtype)
        return self

    def gaussian_sharpen(self, sigma : float, power : float, mask = None) -> 'ImageProcessor':
        """
         sigma  float

         power  float   0 .. 1.0 and higher
        """
        sigma = max(0, sigma)
        if sigma == 0:
            return self

        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        img = cv2.addWeighted(img, 1.0 + power,
                              cv2.GaussianBlur(img, (0, 0), sigma), -power, 0)
        img = np.clip(img, 0, 1, out=img)
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img

        self.to_dtype(dtype)
        return self

    def gaussian_blur(self, sigma : float, opacity : float = 1.0, mask = None) -> 'ImageProcessor':
        """
         sigma  float

         opacity  float   0 .. 1.0
        """
        sigma = max(0, sigma)
        if sigma == 0:
            return self
        opacity = np.float32( min(1, max(0, opacity)) )
        if opacity == 0:
            return self

        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        img_blur = cv2.GaussianBlur(img, (0,0), sigma)
        f32_1 = np.float32(1.0)
        img = ne.evaluate('img*(f32_1-opacity) + img_blur*opacity')

        img = np.clip(img, 0, 1, out=img)
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img

        self.to_dtype(dtype)
        return self

    def median_blur(self, size : int, opacity : float = 1.0, mask = None) -> 'ImageProcessor':
        """
         size   int     median kernel size

         opacity  float   0 .. 1.0
        """
        if size % 2 == 0:
            size += 1
        size = max(1, size)

        opacity = min(1, max(0, opacity))
        if opacity == 0:
            return self

        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        img_blur = cv2.medianBlur(img, size)
        f32_1 = np.float32(1.0)
        img = ne.evaluate('img*(f32_1-opacity) + img_blur*opacity')
        img = np.clip(img, 0, 1, out=img)
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img

        self.to_dtype(dtype)
        return self

    def motion_blur( self, size, angle, mask=None ):
        """
            size [1..]

            angle   degrees

            mask    H,W
                    H,W,C
                    N,H,W,C int/float 0-1 will be applied
        """
        if size % 2 == 0:
            size += 1

        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        k = np.zeros((size, size), dtype=np.float32)
        k[ (size-1)// 2 , :] = np.ones(size, dtype=np.float32)
        k = cv2.warpAffine(k, cv2.getRotationMatrix2D( (size / 2 -0.5 , size / 2 -0.5 ) , angle, 1.0), (size, size) )
        k = k * ( 1.0 / np.sum(k) )

        img = cv2.filter2D(img, -1, k)
        img = np.clip(img, 0, 1, out=img)
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img
        self.to_dtype(dtype)
        return self


    def erode_blur(self, erode : int, blur : int, fade_to_border : bool = False) -> 'ImageProcessor':
        """
        apply erode and blur to the mask image

         erode  int     != 0
         blur   int     > 0
         fade_to_border(False)  clip the image in order
                                to fade smoothly to the border with specified blur amount
        """
        erode, blur = int(erode), int(blur)

        img = self._img
        N,H,W,C = img.shape

        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )
        img = np.pad (img, ( (H,H), (W,W), (0,0) ) )

        if erode > 0:
            el = np.asarray(cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
            iterations = max(1,erode//2)
            img = cv2.erode(img, el, iterations = iterations )

        elif erode < 0:
            el = np.asarray(cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
            iterations = max(1,-erode//2)
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
            img = cv2.GaussianBlur(img, (0, 0), sigma)

        img = img[H:-H,W:-W]
        img = img.reshape( (H,W,N,C) ).transpose( (2,0,1,3) )

        self._img = img
        return self

    def levels(self, in_bwg_out_bw, mask = None) -> 'ImageProcessor':
        """
         in_bwg_out_bw  ( [N],[C], 5)
                        optional per channel/batch input black,white,gamma and out black,white floats

                        in black = [0.0 .. 1.0] default:0.0
                        in white = [0.0 .. 1.0] default:1.0
                        in gamma = [0.0 .. 2.0++] default:1.0

                        out black = [0.0 .. 1.0] default:0.0
                        out white = [0.0 .. 1.0] default:1.0
        """
        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape

        v = np.array(in_bwg_out_bw, np.float32)

        if v.ndim == 1:
            v = v[None,None,...]
            v = np.tile(v, (N,C,1))
        elif v.ndim == 2:
            v = v[None,...]
            v = np.tile(v, (N,1,1))
        elif v.ndim > 3:
            raise ValueError('in_bwg_out_bw.ndim > 3')

        VN, VC, VD = v.shape
        if N != VN or C != VC or VD != 5:
            raise ValueError('wrong in_bwg_out_bw size. Must have 5 floats at last dim.')

        v = v[:,None,None,:,:]

        img = np.clip( (img - v[...,0]) / (v[...,1] - v[...,0]), 0, 1 )

        img = ( img ** (1/v[...,2]) ) *  (v[...,4] - v[...,3]) + v[...,3]
        img = np.clip(img, 0, 1, out=img)

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img
        self.to_dtype(dtype)
        return self

    def hsv(self, h_diff : float, s_diff : float, v_diff : float, mask = None) -> 'ImageProcessor':
        """
        apply HSV modification for BGR image

            h_diff = [-1.0 .. 1.0]
            s_diff = [-1.0 .. 1.0]
            v_diff = [-1.0 .. 1.0]
        """
        dtype = self.get_dtype()
        self.to_ufloat32()

        img = orig_img = self._img
        N,H,W,C = img.shape
        if C != 3:
            raise Exception('Image channels must be == 3')

        img = img.reshape( (N*H,W,C) )

        h, s, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
        h = ( h + h_diff*360.0 ) % 360

        s += s_diff
        np.clip (s, 0, 1, out=s )

        v += v_diff
        np.clip (v, 0, 1, out=v )

        img = np.clip( cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR) , 0, 1 )
        img = img.reshape( (N,H,W,C) )

        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask')

        self._img = img
        self.to_dtype(dtype)
        return self

    def to_lab(self) -> 'ImageProcessor':
        """
        """
        img = self._img
        N,H,W,C = img.shape
        if C != 3:
            raise Exception('Image channels must be == 3')

        img = img.reshape( (N*H,W,C) )
        img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        img = img.reshape( (N,H,W,C) )

        self._img = img
        return self

    def from_lab(self) -> 'ImageProcessor':
        """
        """
        img = self._img
        N,H,W,C = img.shape
        if C != 3:
            raise Exception('Image channels must be == 3')

        img = img.reshape( (N*H,W,C) )
        img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
        img = img.reshape( (N,H,W,C) )

        self._img = img
        return self

    def jpeg_recompress(self, quality : int, mask = None ) -> 'ImageProcessor':
        """
         quality    0-100
        """
        dtype = self.get_dtype()
        self.to_uint8()

        img = orig_img = self._img
        _,_,_,C = img.shape
        if C != 3:
            raise Exception('Image channels must be == 3')

        new_imgs = []
        for x in img:
            ret, result = cv2.imencode('.jpg', x, [int(cv2.IMWRITE_JPEG_QUALITY), quality] )
            if not ret:
                raise Exception('unable to compress jpeg')
            x = cv2.imdecode(result, flags=cv2.IMREAD_UNCHANGED)

            new_imgs.append(x)

        img = np.array(new_imgs)


        if mask is not None:
            mask = self._check_normalize_mask(mask)
            img = ne.evaluate('orig_img*(1-mask) + img*mask').astype(np.uint8)

        self._img = img
        self.to_dtype(dtype)

        return self

    def patch_to_batch(self, patch_size : int) -> 'ImageProcessor':
        img = self._img

        N,H,W,C = img.shape
        OH, OW = H // patch_size, W // patch_size

        img = img.reshape(N,OH,patch_size,OW,patch_size,C)
        img = img.transpose(0,2,4,1,3,5)
        img = img.reshape(N*patch_size*patch_size,OH,OW,C)
        self._img = img

        return self

    def patch_from_batch(self, patch_size : int) -> 'ImageProcessor':
        img = self._img

        N,H,W,C = img.shape
        ON = N//(patch_size*patch_size)
        img = img.reshape(ON,patch_size,patch_size,H,W,C )
        img = img.transpose(0,3,1,4,2,5)
        img = img.reshape(ON,H*patch_size,W*patch_size,C )
        self._img = img

        return self

    def rct(self, like : np.ndarray, mask : np.ndarray = None, like_mask : np.ndarray = None, mask_cutoff=0.5) -> 'ImageProcessor':
        """
        Transfer color using rct method.

            like                np.ndarray [N][HW][3C]  np.uint8/np.float32

            mask(None)          np.ndarray [N][HW][1C]  np.uint8/np.float32
            like_mask(None)     np.ndarray [N][HW][1C]  np.uint8/np.float32

            mask_cutoff(0.5)    float

        masks are used to limit the space where color statistics will be computed to adjust the image

        reference: Color Transfer between Images https://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf
        """
        dtype = self.get_dtype()

        self.to_ufloat32()
        self.to_lab()

        like_for_stat = ImageProcessor(like).to_ufloat32().to_lab().get_image('NHWC')
        if like_mask is not None:
            like_mask = ImageProcessor(like_mask).to_ufloat32().ch(1).get_image('NHW')
            like_for_stat = like_for_stat.copy()
            like_for_stat[like_mask < mask_cutoff] = [0,0,0]

        img_for_stat = img = self._img
        if mask is not None:
            mask = ImageProcessor(mask).to_ufloat32().ch(1).get_image('NHW')
            img_for_stat = img_for_stat.copy()
            img_for_stat[mask < mask_cutoff] = [0,0,0]

        source_l_mean, source_l_std, source_a_mean, source_a_std, source_b_mean, source_b_std, \
            = img_for_stat[...,0].mean((1,2), keepdims=True), img_for_stat[...,0].std((1,2), keepdims=True), img_for_stat[...,1].mean((1,2), keepdims=True), img_for_stat[...,1].std((1,2), keepdims=True), img_for_stat[...,2].mean((1,2), keepdims=True), img_for_stat[...,2].std((1,2), keepdims=True)

        like_l_mean, like_l_std, like_a_mean, like_a_std, like_b_mean, like_b_std, \
            = like_for_stat[...,0].mean((1,2), keepdims=True), like_for_stat[...,0].std((1,2), keepdims=True), like_for_stat[...,1].mean((1,2), keepdims=True), like_for_stat[...,1].std((1,2), keepdims=True), like_for_stat[...,2].mean((1,2), keepdims=True), like_for_stat[...,2].std((1,2), keepdims=True)

        # not as in the paper: scale by the standard deviations using reciprocal of paper proposed factor
        source_l = img[...,0]
        source_l = ne.evaluate('(source_l - source_l_mean) * like_l_std / source_l_std + like_l_mean')

        source_a = img[...,1]
        source_a = ne.evaluate('(source_a - source_a_mean) * like_a_std / source_a_std + like_a_mean')

        source_b = img[...,2]
        source_b = ne.evaluate('(source_b - source_b_mean) * like_b_std / source_b_std + like_b_mean')

        np.clip(source_l,    0, 100, out=source_l)
        np.clip(source_a, -127, 127, out=source_a)
        np.clip(source_b, -127, 127, out=source_b)

        self._img = np.stack([source_l,source_a,source_b], -1)
        self.from_lab()
        self.to_dtype(dtype)
        return self

    def rotate90(self) -> 'ImageProcessor':
        self._img = np.rot90(self._img, k=1, axes=(1,2) )
        return self

    def rotate180(self) -> 'ImageProcessor':
        self._img = np.rot90(self._img, k=2, axes=(1,2) )
        return self

    def rotate270(self) -> 'ImageProcessor':
        self._img = np.rot90(self._img, k=3, axes=(1,2) )
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
        self._img = np.pad(self._img, ( (0,0), (t_h,b_h), (l_w,r_w), (0,0) ))
        return self

    def pad_to_next_divisor(self, dw=None, dh=None) -> 'ImageProcessor':
        """
        pad image to next divisor of width/height

         dw,dh  int
        """
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
            img = np.pad(img, ( (0,0), (0,h_pad), (0,w_pad), (0,0) ))

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

        return np.ascontiguousarray(img)

    def ch(self, TC : int) -> 'ImageProcessor':
        """
        Clips or expands channel dimension to target channels

         TC     int     >= 1
        """
        img = self._img
        N,H,W,C = img.shape

        if TC <= 0:
            raise ValueError(f'channels must be positive value, not {TC}')

        if TC > C:
            # Ch expand
            img = img[...,0:1]  # Clip to single ch first.
            img = np.repeat (img, TC, -1) # Expand by repeat
        elif TC < C:
            # Ch reduction  clip
            img = img[...,:TC]

        self._img = img
        return self

    def to_grayscale(self) -> 'ImageProcessor':
        """
        Converts 3 ch bgr to grayscale.
        """
        img = self._img
        _,_,_,C = img.shape
        if C != 1:
            dtype = self.get_dtype()

            if C == 2:
                img = img[...,:1]
            elif C >= 3:
                img = img[...,:3]

                img = np.dot(img, np.array([0.1140, 0.5870, 0.2989], np.float32)) [...,None]
            img = img.astype(dtype)
            self._img = img

        return self

    def resize(self, size : Tuple, interpolation : 'ImageProcessor.Interpolation' = None ) -> 'ImageProcessor':
        """
        resize to (W,H)
        """
        img = self._img
        N,H,W,C = img.shape

        TW,TH = size
        if W != TW or H != TH:
            if interpolation is None:
                interpolation = ImageProcessor.Interpolation.LINEAR

            img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )
            img = cv2.resize (img, (TW, TH), interpolation=_cv_inter[interpolation])
            img = img.reshape( (TH,TW,N,C) ).transpose( (2,0,1,3) )

            self._img = img

        return self

    def warp_affine(self, mat, out_width, out_height, interpolation : 'ImageProcessor.Interpolation' = None ) -> 'ImageProcessor':
        """
        img    HWC
        """
        img = self._img
        N,H,W,C = img.shape
        img = img.transpose( (1,2,0,3) ).reshape( (H,W,N*C) )

        if interpolation is None:
            interpolation = ImageProcessor.Interpolation.LINEAR

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
        self._img = self._img.astype(np.float32)
        return self

    def as_uint8(self) -> 'ImageProcessor':
        """
        change image format to uint8
        """
        self._img = self._img.astype(np.uint8)
        return self

    def to_dtype(self, dtype, from_tanh=False) -> 'ImageProcessor':
        if dtype == np.float32:
            return self.to_ufloat32(from_tanh=from_tanh)
        elif dtype == np.uint8:
            return self.to_uint8(from_tanh=from_tanh)
        else:
            raise ValueError('unsupported dtype')

    def to_ufloat32(self, as_tanh=False, from_tanh=False) -> 'ImageProcessor':
        """
        Convert to uniform float32
        """
        if self._img.dtype == np.uint8:
            self._img = self._img.astype(np.float32)
            if as_tanh:
                self._img /= 127.5
                self._img -= 1.0
            else:
                self._img /= 255.0
        elif self._img.dtype in [np.float32, np.float64]:
            if from_tanh:
                self._img += 1.0
                self._img /= 2.0

        return self

    def to_uint8(self, from_tanh=False) -> 'ImageProcessor':
        """
        Convert to uint8

        if current image dtype is float32/64, then image will be multiplied by *255
        """
        img = self._img

        if img.dtype in [np.float32, np.float64]:
            if from_tanh:
                img += 1.0
                img /= 2.0

            img *= 255.0
            np.clip(img, 0, 255, out=img)

        self._img = img.astype(np.uint8, copy=False)
        return self

    def _check_normalize_mask(self, mask : np.ndarray):
        N,H,W,C = self._img.shape

        if mask.ndim == 2:
            mask = mask[None,...,None]
        elif mask.ndim == 3:
            mask = mask[None,...]

        if mask.ndim != 4:
            raise ValueError('mask must have ndim == 4')

        MN, MH, MW, MC = mask.shape
        if H != MH or W != MW:
            raise ValueError('mask H,W, mismatch')

        if MN != 1 and N != MN:
            raise ValueError(f'mask N dim must be 1 or == {N}')
        if MC != 1 and C != MC:
            raise ValueError(f'mask C dim must be 1 or == {C}')

        return mask

    class Interpolation(IntEnum):
        NEAREST = 0,
        LINEAR = 1
        CUBIC = 2,
        LANCZOS4 = 4

_cv_inter = { ImageProcessor.Interpolation.NEAREST : cv2.INTER_NEAREST,
              ImageProcessor.Interpolation.LINEAR : cv2.INTER_LINEAR,
              ImageProcessor.Interpolation.CUBIC : cv2.INTER_CUBIC,
              ImageProcessor.Interpolation.LANCZOS4 : cv2.INTER_LANCZOS4,
               }