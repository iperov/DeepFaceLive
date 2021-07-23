from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .QXPixmap import QXPixmap


class QXImage(QImage):
    """
    extension of QImage

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def as_QXPixmap(self) -> QXPixmap:
        pixmap = self._cache.get(QXPixmap, None )
        if pixmap is None:
            pixmap = self._cache[QXPixmap] = QXPixmap(QPixmap.fromImage(self))
        return pixmap

    def as_QIcon(self) -> QIcon:
        icon = self._cache.get(QIcon, None )
        if icon is None:
            icon = self._cache[QIcon] = QIcon(self.as_QXPixmap())
        return icon

    def colored(self, color) -> 'QXImage':
        """
        get colored version from cache or create.
        """
        image = self._cache.get(color, None)
        if image is None:
            pixmap = self.as_QXPixmap()
            qp = QPainter(pixmap)
            qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            qp.fillRect( pixmap.rect(), QColor(color) )
            qp.end()


            image = self._cache[color] = QXImage( pixmap.toImage() )

        return image
