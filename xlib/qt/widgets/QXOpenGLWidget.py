from PyQt6.QtGui import *
from PyQt6.QtOpenGL import *
from PyQt6.QtOpenGLWidgets import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXOpenGLWidget(QOpenGLWidget, _part_QXWidget):
    def __init__(self, **kwargs):
        super().__init__()
        _part_QXWidget.__init__(self, **kwargs)
        self._default_pal = QPalette( self.palette() )

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
