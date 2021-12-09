from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget
from .QXMainApplication import QXMainApplication
from .QXWidget import QXWidget

class QXFrame(QXWidget):
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)

        pal = QXMainApplication.inst.palette()

        if bg_color is not None:
            bg_color = QColor(bg_color)
        else:
            bg_color = pal.color(QPalette.ColorRole.Window)
            bg_color = QColor(bg_color.red()+12,bg_color.green()+12,bg_color.blue()+12,255)

        self._bg_color = bg_color

        self._qp = QPainter()

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)

    def paintEvent(self, ev : QPaintEvent):
        qp = self._qp
        qp.begin(self)
        qp.fillRect(self.rect(), self._bg_color )
        qp.end()
