from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ..core.widget import set_contents_margins


class QXHBoxLayout(QHBoxLayout):
    def __init__(self, widgets=None, contents_margins=0, spacing=0):
        super().__init__()

        set_contents_margins(self, contents_margins)

        if widgets is not None:
            for widget in widgets:
                alignment = None
                if isinstance(widget, int):
                    thickness=widget
                    widget = QWidget()
                    widget.setFixedWidth(thickness)
                    widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

                if isinstance(widget, (tuple,list)):
                    widget, alignment = widget

                if isinstance(widget, QLayout):
                    self.addLayout(widget)
                else:
                    self.addWidget(widget)
                if alignment is not None:
                    self.setAlignment(widget, alignment)
        if spacing is not None:
            self.setSpacing(spacing)
