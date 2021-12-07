from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from .QXFrame import QXFrame
from .QXHBoxLayout import QXHBoxLayout
from .QXLabel import QXLabel
from .QXToolButton import QXToolButton
from .QXVBoxLayout import QXVBoxLayout
from .QXFrameVBox import QXFrameVBox
from .QXFrameHBox import QXFrameHBox

class QXCollapsibleSection(QXFrame):
    """
    Collapsible section.

    Open/close state is saved to app db.
    """
    def __init__(self, title, content_layout, vertical=False, is_opened=True, allow_open_close=True):

        self._is_opened = is_opened
        self._vertical = vertical

        if vertical:
            title = '\n'.join(title)

        label_title = self.label_title = QXLabel(text=title)

        btn = self.btn = QXToolButton(checkable=True, checked=False)
        btn.setStyleSheet('border: none;')
        btn.setArrowType(Qt.ArrowType.RightArrow)

        if allow_open_close:
            btn.toggled.connect(self.on_btn_toggled)

        frame = self.frame = QXFrame(layout=content_layout, size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), hided=True)

        if vertical:
            main_l = QXHBoxLayout([ ( QXFrameVBox([ (btn, Qt.AlignmentFlag.AlignTop),
                                                    (label_title, Qt.AlignmentFlag.AlignCenter)
                                                  ], size_policy=('fixed', 'fixed') ), Qt.AlignmentFlag.AlignTop),
                                    frame])
        else:
            main_l = QXVBoxLayout( [ ( QXFrameHBox([ (btn, Qt.AlignmentFlag.AlignTop),
                                                     (label_title, Qt.AlignmentFlag.AlignCenter)
                                                   ], size_policy=('fixed', 'fixed')) , Qt.AlignmentFlag.AlignTop),
                                    frame])
        super().__init__(layout=main_l)

        if self._is_opened:
            self.open()

    def _on_registered(self):
        super()._on_registered()
        self._is_opened = self.get_widget_data( (QXCollapsibleSection,'opened'), default_value=self._is_opened )
        if self._is_opened:
            self.open()
        else:
            self.close()

    def is_opened(self):
        return self.btn.isChecked()

    def open(self):
        self.set_widget_data( (QXCollapsibleSection,'opened'), True)
        self.btn.setArrowType(Qt.ArrowType.DownArrow)
        self.btn.setChecked(True)
        self.frame.show()

    def close(self):
        self.set_widget_data( (QXCollapsibleSection,'opened'), False)
        self.btn.setArrowType(Qt.ArrowType.RightArrow)
        self.btn.setChecked(False)
        self.frame.hide()

    def on_btn_toggled(self):
        if self.btn.isChecked():
            self.open()
        else:
            self.close()
