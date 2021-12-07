from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget
from typing import List

class QXComboBox(QComboBox, _part_QXWidget):
    def __init__(self, choices : List[str] = None, on_index_changed=None, **kwargs):
        super().__init__()
        [ self.addItem(choice) for choice in choices ] if choices is not None else []
        _part_QXWidget.connect_signal(on_index_changed, self.currentIndexChanged)
        _part_QXWidget.__init__(self, **kwargs)

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
