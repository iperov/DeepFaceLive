from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXToolButton(QToolButton, _part_QXWidget):
    def __init__(self, text=None,
                       checkable=False,
                       checked=None,
                       toggled=None, released=None,
                       **kwargs):
        super().__init__()
        _part_QXWidget.__init__(self, **kwargs)
        _part_QXWidget.connect_signal(released, self.released)
        _part_QXWidget.connect_signal(toggled, self.toggled)

        if text is not None:
            self.setText(text)

        self.setCheckable(checkable)
        if checked is not None:
            self.setChecked(checked)

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
