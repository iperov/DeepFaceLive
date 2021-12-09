from typing import Union

from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import qt as qtx


class QLabelPopupInfo(qtx.QXWidget):
    def __init__(self, label : str = None, popup_info_text = None):
        """
        text label with optional popup info on click
        """
        super().__init__()

        self._has_info_text = False

        self._label = qtx.QXLabel(text='', hided=True)

        wnd_text_label = self._popup_wnd_text_label = qtx.QXLabel(text='', font=QXFontDB.get_default_font() )

        wnd = self._popup_wnd = qtx.QXPopupWindow(layout=qtx.QXHBoxLayout([
                       qtx.QXFrame(bg_color= qtx.Qt.GlobalColor.black,
                                   layout=qtx.QXHBoxLayout([
                                          qtx.QXFrame(layout=qtx.QXHBoxLayout([qtx.QXLabel(image=QXImageDB.information_circle_outline('yellow'), scaled_contents=True, fixed_size=(24,24)),
                                                                               wnd_text_label
                                                                              ], contents_margins=2, spacing=2)),
                       ], contents_margins=2, spacing=2), size_policy=('fixed', 'fixed') )
                     ], contents_margins=0) )

        info_btn = self._info_btn = qtx.QXPushButton(image=QXImageDB.information_circle_outline('light gray'), released=self._on_info_btn_released, fixed_size=(24,22), hided=True)

        self.setLayout(qtx.QXHBoxLayout([self._label, info_btn]))

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

            screen_size = qtx.QXMainApplication.inst.primaryScreen().size()
            label_size = label_widget.size()
            global_pt = label_widget.mapToGlobal( qtx.QPoint(0, label_size.height()))
            popup_wnd_size = popup_wnd.size()
            global_pt = qtx.QPoint( min(global_pt.x(), screen_size.width() - popup_wnd_size.width()),
                                    min(global_pt.y(), screen_size.height() - popup_wnd_size.height()) )

            popup_wnd.move(global_pt)

