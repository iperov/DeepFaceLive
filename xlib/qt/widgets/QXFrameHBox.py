from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .QXFrame import QXFrame
from .QXHBoxLayout import QXHBoxLayout

class QXFrameHBox(QXFrame):
    def __init__(self, widgets=None, contents_margins=0, spacing=0, **kwargs):
        super().__init__(layout=QXHBoxLayout(widgets=widgets, contents_margins=contents_margins, spacing=spacing), **kwargs)
