import numpy as np
from PyQt6.QtGui import *
from ...image import ImageProcessor


def QPixmap_from_np(image : np.ndarray):
    ip = ImageProcessor(image).to_uint8()
    N,H,W,C = ip.get_dims()

    if N > 1:
        raise ValueError(f'N dim must be == 1')

    if C == 1:
        format = QImage.Format.Format_Grayscale8
    elif C == 3:
        format = QImage.Format.Format_BGR888
    elif C == 4:
        format = QImage.Format.Format_ARGB32
    else:
        raise ValueError(f'Unsupported channels {C}')

    image = ip.get_image('HWC')
    q_image = QImage(image.data, W, H, W*C, format)
    q_pixmap = QPixmap.fromImage(q_image)
    return q_pixmap
