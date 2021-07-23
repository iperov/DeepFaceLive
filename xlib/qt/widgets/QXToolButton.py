from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXToolButton(QToolButton, _part_QXWidget):

    def __init__(self, text=None,
                       checkable=False,
                       toggled=None, released=None,
                       font=None, size_policy=None, hided=False, enabled=True):
        super().__init__()

        if text is not None:
            self.setText(text)

        self.setCheckable(checkable)

        _part_QXWidget.connect_signal(released, self.released)
        _part_QXWidget.connect_signal(toggled, self.toggled)
        _part_QXWidget.__init__(self, font=font, size_policy=size_policy, hided=hided, enabled=enabled )


    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
