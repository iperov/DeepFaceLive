from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget


class QXSlider(QSlider, _part_QXWidget):

    def __init__(self, orientation=None,
                       min=None, max=None,
                       tick_position=None,
                       tick_interval=None,
                       valueChanged=None,
                       sliderMoved=None,
                       sliderPressed=None,
                       sliderReleased=None,
                       size_policy=None, hided=False, enabled=True):
        if orientation is not None:
            super().__init__(orientation)
        else:
            super().__init__()

        if min is not None:
            self.setMinimum(min)
        if max is not None:
            self.setMaximum(max)
        if tick_position is not None:
            self.setTickPosition(tick_position)
        if tick_interval is not None:
            self.setTickInterval(tick_interval)

        _part_QXWidget.connect_signal(valueChanged, self.valueChanged)
        _part_QXWidget.connect_signal(sliderMoved, self.sliderMoved)
        _part_QXWidget.connect_signal(sliderPressed, self.sliderPressed)
        _part_QXWidget.connect_signal(sliderReleased, self.sliderReleased)
        _part_QXWidget.__init__(self, size_policy=size_policy, hided=hided, enabled=enabled )


    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
