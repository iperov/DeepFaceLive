from PyQt6.QtWidgets import *

from .QXLabel import QXLabel


class QXHorizontalLine(QXLabel):
    def __init__(self, thickness=1,
                       color=None):

        super().__init__(size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed),
                         fixed_size=(None,thickness) )
        if color is not None:
            self.setStyleSheet(f'background: {color};')
