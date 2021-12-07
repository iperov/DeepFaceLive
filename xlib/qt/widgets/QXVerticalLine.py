from PyQt6.QtWidgets import *

from .QXLabel import QXLabel


class QXVerticalLine(QXLabel):
    def __init__(self, thickness=1, color=None):
        super().__init__(size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding),
                         fixed_size=(thickness,None) )
        if color is not None:
            self.setStyleSheet(f'background: {color.name()};')
