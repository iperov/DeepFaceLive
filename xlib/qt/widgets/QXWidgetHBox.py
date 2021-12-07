from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .QXWidget import QXWidget
from .QXHBoxLayout import QXHBoxLayout

class QXWidgetHBox(QXWidget):
    def __init__(self, widgets=None, contents_margins=0, spacing=0, **kwargs):
        super().__init__(layout=QXHBoxLayout(widgets=widgets, contents_margins=contents_margins, spacing=spacing), **kwargs)
