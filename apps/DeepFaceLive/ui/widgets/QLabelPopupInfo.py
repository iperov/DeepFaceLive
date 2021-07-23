from typing import Union

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import qt as lib_qt


class QLabelPopupInfo(lib_qt.QXWidget):
    """
    text label with optional popup info on click
    """
    def __init__(self, label : str = None, popup_info_text = None):
        super().__init__()

        self._has_info_text = False

        self._label = lib_qt.QXLabel(text='')
        self._label.hide()

        wnd = self._popup_wnd = lib_qt.QXWindow()
        wnd.setParent(self)
        wnd.setWindowFlags(Qt.WindowType.Popup)

        info_btn = self._info_btn = lib_qt.QXPushButton(image=QXImageDB.information_circle_outline('light gray'), fixed_size=(24,22), released=self._on_info_btn_released)
        info_btn.hide()

        wnd_text_label = self._popup_wnd_text_label = lib_qt.QXLabel(text='', font=QXFontDB.get_default_font() )

        wnd_layout = lib_qt.QXHBoxLayout([
                       lib_qt.QXFrame(
                       bg_color= Qt.GlobalColor.black,
                       layout=lib_qt.QXHBoxLayout([

                         lib_qt.QXFrame(layout=lib_qt.QXHBoxLayout([lib_qt.QXLabel(image=QXImageDB.information_circle_outline('yellow'), scaled_contents=True, fixed_size=(24,24)),
                                                                    wnd_text_label
                                                                    ], contents_margins=2, spacing=2)),
                       ], contents_margins=2, spacing=2), size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) )
                     ], contents_margins=0)

        wnd.setLayout(wnd_layout)

        self.setLayout(lib_qt.QXHBoxLayout([self._label, info_btn]))

        self.set_label( label )
        self.set_popup_info( popup_info_text )

    def set_info_icon(self):
        self._label.hide()
        self._info_btn.show()

    def set_label(self, label : Union[str, None]):
        self._info_btn.hide()
        self._label.setText(label)
        self._label.show()

    def set_popup_info(self, text : Union[str, None]):
        if text is not None:
            self._has_info_text = True
            self._popup_wnd_text_label.setText(text)
        else:
            self._has_info_text = False

    def enterEvent(self, ev):
        super().enterEvent(ev)
        if self.isEnabled() and self._has_info_text:
            self._label.set_color('yellow')

    def leaveEvent(self, ev):
        super().leaveEvent(ev)
        if self.isEnabled() and self._has_info_text:
            self._label.set_color(None)

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        self._show_popup_wnd()

    def _on_info_btn_released(self):
        self._show_popup_wnd()

    def _show_popup_wnd(self):

        if self._has_info_text:
            popup_wnd = self._popup_wnd
            popup_wnd.show()

            label_widget = self._label
            if label_widget.isHidden():
                label_widget = self._info_btn

            screen_size = lib_qt.QXMainApplication.get_singleton().primaryScreen().size()
            label_size = label_widget.size()
            global_pt = label_widget.mapToGlobal( QPoint(0, label_size.height()))
            popup_wnd_size = popup_wnd.size()
            global_pt = QPoint( min(global_pt.x(), screen_size.width() - popup_wnd_size.width()),
                                min(global_pt.y(), screen_size.height() - popup_wnd_size.height()) )

            popup_wnd.move(global_pt)

