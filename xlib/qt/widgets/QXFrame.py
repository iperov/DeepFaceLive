from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget
from .QXMainApplication import QXMainApplication


class QXFrame(QFrame, _part_QXWidget):
    def __init__(self, bg_color=None, layout=None, minimum_width=None, maximum_width=None, fixed_width=None, minimum_height=None, maximum_height=None, fixed_height=None, size_policy=None, hided=False, enabled=True):
        QFrame.__init__(self)

        _part_QXWidget.__init__(self, layout=layout,
                                      size_policy=size_policy,
                                      minimum_width=minimum_width, maximum_width=maximum_width,
                                      minimum_height=minimum_height, maximum_height=maximum_height,
                                      fixed_width=fixed_width, fixed_height=fixed_height,
                                      hided=hided, enabled=enabled )

        pal = QXMainApplication.get_singleton().palette()

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
        rect = self.rect()
        qp = self._qp
        qp.begin(self)

        qp.fillRect(rect, self._bg_color )

        qp.end()
