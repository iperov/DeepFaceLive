from typing import Union

import numpy as np
from PyQt6.QtGui import *

from ...image import ImageProcessor, get_NHWC_shape

_C_to_Format = {
    1: QImage.Format.Format_Grayscale8,
    3: QImage.Format.Format_BGR888,
    4: QImage.Format.Format_ARGB32
    }

def QPixmap_from_np(image : np.ndarray):
    """
    constructs QPixmap from image np.ndarray
    """
    if image.dtype != np.uint8:
        raise ValueError('image.dtype must be np.uint8')

    N,H,W,C = get_NHWC_shape(image)
    if N != 1:
        raise ValueError('image N must == 1')
        
    format = _C_to_Format.get(C, None)
    if format is None:
        raise ValueError(f'Unsupported channels {C}')

    q_image = QImage(image.data, W, H, W*C, format)
    q_pixmap = QPixmap.fromImage(q_image)
    return q_pixmap

def QImage_from_np(image : np.ndarray):
    """
    constructs QImage from image np.ndarray

    given image must live the whole life cycle of QImage.
    """
    if image.dtype != np.uint8:
        raise ValueError('image.dtype must be np.uint8')

    N,H,W,C = get_NHWC_shape(image)
    if N != 1:
        raise ValueError('image N must == 1')
    format = _C_to_Format.get(C, None)
    if format is None:
        raise ValueError(f'Unsupported channels {C}')
    return QImage(image.data, W, H, W*C, format)

def QImage_BGR888_from_buffer(buffer : Union[bytes, bytearray], width : int, height : int ):

    """
    constructs QImage of BGR888 format from byte buffer with given width,height

    given buffer must live the whole life cycle of QImage.
    """
    if len(buffer) != width*height*3:
        raise ValueError(f'Size of buffer must be width*height*3 == {width*height*3}')

    return QImage(buffer, width, height, width*3, QImage.Format.Format_BGR888)

def QImage_ARGB32_from_buffer(buffer : Union[bytes, bytearray], width : int, height : int ):

    """
    constructs QImage of ARGB32 format from byte buffer with given width,height

    given buffer must live the whole life cycle of QImage.
    """
    if len(buffer) != width*height*4:
        raise ValueError(f'Size of buffer must be width*height*4 == {width*height*4}')

    return QImage(buffer, width, height, width*3, QImage.Format.Format_ARGB32)
