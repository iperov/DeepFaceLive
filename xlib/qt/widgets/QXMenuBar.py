from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXMenuBar(QMenuBar, _part_QXWidget):
    def __init__(self,
                       font=None, size_policy=None, minimum_width=None, maximum_width=None, fixed_width=None, minimum_height=None, maximum_height=None, fixed_height=None, hided=False, enabled=True):
        QMenuBar.__init__(self)

        _part_QXWidget.__init__(self, font=font,
                                      size_policy=size_policy,
                                      minimum_width=minimum_width, maximum_width=maximum_width,
                                      minimum_height=minimum_height, maximum_height=maximum_height,
                                      fixed_width=fixed_width, fixed_height=fixed_height,
                                      hided=hided, enabled=enabled )

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
