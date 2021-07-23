from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXLineEdit(QLineEdit, _part_QXWidget):
    def __init__(self, placeholder_text=None,
                       style_sheet=None,
                       read_only=False,
                       editingFinished=None,
                       font=None, size_policy=None, hided=False, enabled=True):

        super().__init__()
        if placeholder_text is not None:
            self.setPlaceholderText(placeholder_text)

        if style_sheet is not None:
            self.setStyleSheet(style_sheet)
        if read_only:
            self.setReadOnly(True)

        _part_QXWidget.connect_signal(editingFinished, self.editingFinished)
        _part_QXWidget.__init__(self, font=font, size_policy=size_policy, hided=hided, enabled=enabled )

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
