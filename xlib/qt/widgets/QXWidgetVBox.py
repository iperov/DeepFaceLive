from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .QXWidget import QXWidget
from .QXVBoxLayout import QXVBoxLayout

class QXWidgetVBox(QXWidget):
    def __init__(self, widgets=None, contents_margins=0, spacing=0, **kwargs):
        super().__init__(layout=QXVBoxLayout(widgets=widgets, contents_margins=contents_margins, spacing=spacing), **kwargs)
