from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXSpinBox(QSpinBox, _part_QXWidget):
    def __init__(self, min=None,
                       max=None,
                       step=None,
                       special_value_text=None,
                       color=None,
                       alignment=None,
                       button_symbols=None, readonly=False,
                       editingFinished=None, textChanged=None, valueChanged=None,
                       font=None, size_policy=None, hided=False, enabled=True):
        super().__init__()
        if min is not None:
            self.setMinimum(min)
        if max is not None:
            self.setMaximum(max)
        if step is not None:
            self.setSingleStep(step)
        if special_value_text is not None:
            self.setSpecialValueText(special_value_text)
        if alignment is not None:
            self.setAlignment(alignment)
        if button_symbols is not None:
            self.setButtonSymbols(button_symbols)
        self.setReadOnly(readonly)

        if color is not None:
            self.setStyleSheet(f'QSpinBox {{ color: {color};}}')

        _part_QXWidget.connect_signal(editingFinished, self.editingFinished)
        _part_QXWidget.connect_signal(textChanged, self.textChanged)
        _part_QXWidget.connect_signal(valueChanged, self.valueChanged)
        _part_QXWidget.__init__(self, font=font, size_policy=size_policy, hided=hided, enabled=enabled )


    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
