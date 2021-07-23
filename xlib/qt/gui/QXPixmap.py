from PyQt6.QtCore import *
from PyQt6.QtGui import *


class QXPixmap(QPixmap):
    """
    extension of QPixmap

    contains cached scaled versions
    cached grayscaled
    cached QIcon
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def scaled_cached(self, width: int, height: int, aspectRatioMode: Qt.AspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio) -> 'QPixmap':
        """
        get scaled version from cache or create.
        """
        key = (width, height)
        pixmap = self._cache.get(key, None)

        if pixmap is None:
            pixmap = self._cache[key] = QXPixmap( self.scaled(width, height, aspectRatioMode=aspectRatioMode, transformMode=Qt.TransformationMode.SmoothTransformation) )

        return pixmap


    def as_QIcon(self) -> QIcon:
        icon = self._cache.get( QIcon, None )
        if icon is None:
            icon = self._cache[QIcon] = QIcon(self)
        return icon


    def grayscaled_cached(self) -> 'QXPixmap':
        """
        get grayscaled version from cache or create.
        """
        key = 'grayscaled'
        pixmap = self._cache.get(key, None)
        if pixmap is None:
            pixmap = QXPixmap(self)
            qp = QPainter(pixmap)
            qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            qp.fillRect( pixmap.rect(), QColor(127,127,127,255) )
            qp.end()
            pixmap = self._cache[key] = pixmap

        return pixmap
