from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXTextEdit(QTextEdit, _part_QXWidget):
    def __init__(self, placeholder_text=None,
                       style_sheet=None,
                       read_only=False,
                       
                       font=None, tooltip_text=None,
                       size_policy=None,
                       minimum_size=None, minimum_width=None, minimum_height=None,
                       maximum_size=None, maximum_width=None, maximum_height=None,
                       fixed_size=None, fixed_width=None, fixed_height=None,
                       hided=False, enabled=True
                       ):

        super().__init__()
        if placeholder_text is not None:
            self.setPlaceholderText(placeholder_text)

        if style_sheet is not None:
            self.setStyleSheet(style_sheet)
        if read_only:
            self.setReadOnly(True)
        self.setWordWrapMode
        #_part_QXWidget.connect_signal(editingFinished, self.editingFinished)
        _part_QXWidget.__init__(self,   font=font, tooltip_text=tooltip_text,
                                        size_policy=size_policy,
                                        minimum_size=minimum_size, minimum_width=minimum_width, minimum_height=minimum_height,
                                        maximum_size=maximum_size, maximum_width=maximum_width, maximum_height=maximum_height,
                                        fixed_size=fixed_size, fixed_width=fixed_width, fixed_height=fixed_height,
                                        hided=hided, enabled=enabled )

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
