from localization import L
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB, QXImageSequenceDB
from xlib import qt as qtx

from ...backend import BackendHost


class QBackendPanel(qtx.QXWidget):
    """
    Base panel for CSW backend
    """
    def __init__(self, backend : BackendHost, name : str, layout, content_align_top=False):
        super().__init__()
        if not isinstance(backend, BackendHost):
            raise ValueError('backend must be an instance of BackendHost')

        self._backend = backend
        self._name = name

        backend.call_on_state_change(self._on_backend_state_change)
        backend.call_on_profile_timing(self._on_backend_profile_timing)

        btn_on_off = self._btn_on_off = qtx.QXPushButton(tooltip_text=L('@QBackendPanel.start'),
                                                         released=self._on_btn_on_off_released,
                                                         fixed_width=20)

        btn_reset_state = self._btn_reset_state = qtx.QXPushButton(image=QXImageDB.settings_reset_outline('gray'),
                                                                   released=self._on_btn_reset_state_released, tooltip_text=L('@QBackendPanel.reset_settings'),
                                                                   fixed_width=20)

        fps_label = self._fps_label = qtx.QXLabel()

        bar_widget = self._bar_widget = \
            qtx.QXFrameHBox(widgets=[btn_on_off, 1, btn_reset_state, 2,
                                     qtx.QXLabel(name, font=QXFontDB.get_default_font(10)),
                                     (fps_label, qtx.AlignRight), 2],
                            size_policy=('expanding', 'fixed'), fixed_height=24)

        content_widget = self._content_widget = qtx.QXFrameHBox([layout], contents_margins=2, enabled=False)

        l_widgets = [bar_widget, 1]

        if not content_align_top:
            l_widgets += [ qtx.QXFrame(size_policy=('expanding','expanding') ) ]

        l_widgets += [content_widget]
        l_widgets += [ qtx.QXFrame(size_policy=('expanding', 'expanding') ) ]

        self.setLayout(qtx.QXVBoxLayout(l_widgets))

        btn_on_off.set_image( QXImageDB.power_outline('red') )

    def _on_backend_state_change(self, backend, started, starting, stopping, stopped, busy):
        btn_on_off = self._btn_on_off

        if started or starting or stopping:
            btn_on_off.setToolTip(L('@QBackendPanel.stop'))
        if stopped:
            btn_on_off.setToolTip(L('@QBackendPanel.start'))

        if busy or starting or stopping:
            btn_on_off.set_image_sequence(QXImageSequenceDB.icon_loading('yellow'), loop_count=0)
        elif started:
            btn_on_off.set_image( QXImageDB.power_outline('lime') )
        elif stopped:
            btn_on_off.set_image( QXImageDB.power_outline('red') )

        if started and not busy:
            qtx.show_and_enable([self._content_widget, self._fps_label])
            self._fps_label.setText(None)
        else:
            qtx.hide_and_disable([self._content_widget, self._fps_label])
            self._fps_label.setText(None)

    def _on_backend_profile_timing(self, timing : float):
        fps = int(1.0 / timing if timing != 0 else 0)
        if fps < 10:
            self._fps_label.set_color('red')
        else:
            self._fps_label.set_color(None)
        self._fps_label.setText(f"{fps} {L('@QBackendPanel.FPS')}")

    def _on_btn_on_off_released(self):
        backend = self._backend
        if backend.is_stopped():
            backend.start()
        else:
            backend.stop()

    def _on_btn_reset_state_released(self):
        self._backend.reset_state()
