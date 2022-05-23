from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from .QXWindow import QXWindow

class QXPopupWindow(QXWindow):
    def __init__(self, **kwargs):
        """
        represents top widget which has no parent
        """
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Popup)
       
