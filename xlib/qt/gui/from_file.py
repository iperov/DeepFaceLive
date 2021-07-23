from PyQt6.QtGui import *

from .QXImage import QXImage
from .QXPixmap import QXPixmap


def QPixmap_from_file(filepath, color=None):
    img = QPixmap(str(filepath))

    if color is not None:
        qp = QPainter(img)
        qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        qp.fillRect( img.rect(), QColor(color) )
        qp.end()
    return img

def QXPixmap_from_file(filepath, color=None):
    img = QXPixmap(str(filepath))

    if color is not None:
        qp = QPainter(img)
        qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        qp.fillRect( img.rect(), QColor(color) )
        qp.end()
    return img

def QXImage_from_file(filepath, color=None):
    return QXImage(QPixmap_from_file(filepath, color).toImage())


def QIcon_from_file(filepath, color='black'):
    return QIcon(QPixmap_from_file(filepath,color=color))
