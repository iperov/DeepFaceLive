from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXMenuBar(QMenuBar, _part_QXWidget):
    def __init__(self, **kwargs):
        QMenuBar.__init__(self)
        _part_QXWidget.__init__(self, **kwargs)
        self.setStyleSheet(f"""
QMenuBar {{
    border: 0px;
    background-color: #444444;
}}
""")

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
