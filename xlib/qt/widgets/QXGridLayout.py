from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ..core.widget import set_contents_margins


class QXGridLayout(QGridLayout):
    def __init__(self, contents_margins=0, spacing=None, horizontal_spacing=None, vertical_spacing=None):
        super().__init__()
        set_contents_margins(self, contents_margins)

        if spacing is not None:
            self.setSpacing(spacing)

        if horizontal_spacing is not None:
            self.setHorizontalSpacing(horizontal_spacing)

        if vertical_spacing is not None:
            self.setVerticalSpacing(vertical_spacing)

