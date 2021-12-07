from typing import List, Union

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ..gui.from_np import QImage_from_np
from .QXWidget import QXWidget


class QXFixedLayeredImages(QXWidget):
    """
    A widget to show multiple stacked images in fixed area

    all images must have the same aspect ratio
    """
    def __init__(self, fwidth, height):
        super().__init__()
        self._fwidth = fwidth
        self._height = height
        self._qp = QPainter()
        self._images : List = []

    def clear_images(self):
        self._images : List = []
        self.update()

    def add_image(self, image, name=None):
        """
         image  QImage
                QPixmap
                np.ndarray  of uint8 dtype
        """
        saved_ref = None

        if not isinstance(image, QImage) and not isinstance(image, QPixmap):
            if isinstance(image, np.ndarray):
                saved_ref = image
                image = QImage_from_np(image)
            else:
                raise ValueError(f'Unsupported type of image {image.__class__}')

        self._images.append( (image, saved_ref) )
        self.update()

    def sizeHint(self):
        return QSize(self._fwidth, self._height)

    def paintEvent(self, event):
        super().paintEvent(event)

        qp = self._qp
        qp.begin(self)
        qp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = self._fwidth
        h = self._height

        w_half = w /2
        h_half = h /2
        a = w/h

        for image, _ in self._images:

            size = image.size()
            ap = size.width() / size.height()

            if ap > a:
                ph_fit = h * (a / ap)
                rect = QRect(0, h_half-ph_fit/2, w, ph_fit )
            elif ap < a:
                pw_fit = w * (ap / a)
                rect = QRect(w_half-pw_fit/2, 0, pw_fit, h )
            else:
                rect = self.rect()

            if isinstance(image, QImage):
                qp.drawImage(rect, image, image.rect())
            elif isinstance(image, QPixmap):
                qp.drawPixmap(rect, image, image.rect())

        qp.end()
