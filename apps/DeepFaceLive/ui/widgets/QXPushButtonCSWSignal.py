from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QXPushButtonCSWSignal(QCSWControl):
    """
    Implements lib_csw.Signal control as PushButton
    """
    def __init__(self,  csw_signal : lib_csw.Signal.Client, reflect_state_widgets=None,
                        image=None,
                        text=None, button_size=None, button_height=None,):

        if not isinstance(csw_signal, lib_csw.Signal.Client):
            raise ValueError('csw_signal must be an instance of Signal.Client')
        super().__init__(csw_control=csw_signal, reflect_state_widgets=reflect_state_widgets)
        self._csw_signal = csw_signal

        # Init UI
        btn = self._btn = lib_qt.QXPushButton(image=image, text=text, released=self.on_btn_released, minimum_size=button_size, minimum_height=button_height)

        main_l = lib_qt.QXHBoxLayout([btn])

        self.setLayout(main_l)
        self.hide()

    def on_btn_released(self):
        self._csw_signal.signal()
