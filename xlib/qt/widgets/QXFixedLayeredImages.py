from typing import List

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib.image import ImageProcessor
from ..gui.from_np import QPixmap_from_np
from .QXWidget import QXWidget


class QXFixedLayeredImages(QXWidget):
    """
    A widget to show multiple stacked images in fixed area
    """
    def __init__(self, fixed_width, fixed_height):
        super().__init__()
        self._fixed_width = fixed_width
        self._fixed_height = fixed_height
        self._qp = QPainter()
        self._pixmaps : List[QPixmap] = []

    def clear_images(self):
        self._pixmaps : List[QPixmap] = []
        self.update()

    def add_image(self, image, name=None):
        """
         image  np.ndarray
                QPixmap

        all images must have the same aspect ratio
        """
        if isinstance(image, np.ndarray):
            ip = ImageProcessor(image)
            ip.fit_in(self._fixed_width, self._fixed_height)
            image = ip.get_image('HWC')
            q_pixmap = QPixmap_from_np(image)
        elif isinstance(image, QPixmap):
            q_pixmap = image
        else:
            raise ValueError(f'Unsupported type of image {image.__class__}')

        self._pixmaps.append(q_pixmap)
        self.update()

    def sizeHint(self):
        return QSize(self._fixed_width, self._fixed_height)

    def paintEvent(self, event):
        super().paintEvent(event)

        qp = self._qp
        qp.begin(self)
        #qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = self._fixed_width
        h = self._fixed_height

        w_half = w /2
        h_half = h /2
        a = w/h

        for pixmap in self._pixmaps:
            size = pixmap.size()
            ap = size.width() / size.height()

            if ap > a:
                ph_fit = h * (a / ap)
                rect = QRect(0, h_half-ph_fit/2, w, ph_fit )
            elif ap < a:
                pw_fit = w * (ap / a)
                rect = QRect(w_half-pw_fit/2, 0, pw_fit, h )
            else:
                rect = self.rect()

            qp.drawPixmap(rect, pixmap, pixmap.rect())

        qp.end()
