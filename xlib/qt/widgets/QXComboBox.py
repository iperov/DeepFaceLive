from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget
from typing import List

class QXComboBox(QComboBox, _part_QXWidget):
    def __init__(self, choices : List[str] = None,
                       on_index_changed=None,
                       font=None, tooltip_text=None,
                       minimum_width=None, maximum_width=None, fixed_width=None, minimum_height=None, maximum_height=None, fixed_height=None, size_policy=None, hided=False, enabled=True):
        super().__init__()

        if choices is not None:
            for choice in choices:
                self.addItem(choice)

        _part_QXWidget.connect_signal(on_index_changed, self.currentIndexChanged)
        _part_QXWidget.__init__(self, font=font, tooltip_text=tooltip_text,
                                      size_policy=size_policy,
                                      minimum_width=minimum_width, maximum_width=maximum_width,
                                      minimum_height=minimum_height, maximum_height=maximum_height,
                                      fixed_width=fixed_width, fixed_height=fixed_height,
                                      hided=hided, enabled=enabled )

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
