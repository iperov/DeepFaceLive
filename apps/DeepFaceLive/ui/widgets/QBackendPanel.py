from localization import L
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB, QXImageSequenceDB
from xlib import qt as lib_qt

from ...backend import BackendHost


class QBackendPanel(lib_qt.QXWidget):
    """
    Base panel for CSW backend
    """
    def __init__(self, backend : BackendHost, name : str, layout, content_align_top=False):
        if not isinstance(backend, BackendHost):
            raise ValueError('backend must be an instance of BackendHost')

        super().__init__()
        self._backend = backend
        self._name = name

        backend.call_on_state_change(self._on_backend_state_change)
        backend.call_on_profile_timing(self._on_backend_profile_timing)

        btn_on_off = self._btn_on_off = lib_qt.QXPushButton(tooltip_text=L('@QBackendPanel.start'), fixed_width=20, released=self._on_btn_on_off_released)

        btn_reset_state = self._btn_reset_state = lib_qt.QXPushButton(image=QXImageDB.settings_reset_outline('gray'),
                                                                    #size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum),
                                                                    fixed_width=20,  released=self._on_btn_reset_state_released, tooltip_text=L('@QBackendPanel.reset_settings') )

        timing_label = self._timing_label = lib_qt.QXLabel()

        bar_widget = self._bar_widget = \
            lib_qt.QXFrame(layout=lib_qt.QXHBoxLayout([
                              lib_qt.QXWidget(layout=lib_qt.QXHBoxLayout([
                                                 btn_on_off,
                                                 1,
                                                 btn_reset_state,
                                                 2,
                                                 lib_qt.QXLabel(name, font=QXFontDB.get_default_font(10)),

                                                 (timing_label, Qt.AlignmentFlag.AlignRight),
                                                 2
                                                ]), fixed_height=24),
                              ]),
                           size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) )

        content_widget = self._content_widget = lib_qt.QXFrame(layout=lib_qt.QXHBoxLayout([layout], contents_margins=2),
                                                               enabled=False )

        l_widgets = [bar_widget, 1]

        if not content_align_top:
            l_widgets += [ lib_qt.QXFrame(size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) ) ]

        l_widgets += [content_widget]
        l_widgets += [ lib_qt.QXFrame(size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) ) ]

        self.setLayout(lib_qt.QXVBoxLayout(l_widgets))

        lib_qt.disable([self._content_widget])
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
            lib_qt.show_and_enable([self._content_widget, self._timing_label])
            self._timing_label.setText(None)
        else:
            lib_qt.hide_and_disable([self._content_widget, self._timing_label])
            self._timing_label.setText(None)

    def _on_backend_profile_timing(self, timing : float):
        fps = int(1.0 / timing if timing != 0 else 0)
        if fps < 10:
            self._timing_label.set_color('red')
        else:
            self._timing_label.set_color(None)
        self._timing_label.setText(f"{fps} {L('@QBackendPanel.FPS')}")

    def _on_btn_on_off_released(self):
        backend = self._backend
        if backend.is_stopped():
            backend.start()
        else:
            backend.stop()

    def _on_btn_reset_state_released(self):
        self._backend.reset_state()
