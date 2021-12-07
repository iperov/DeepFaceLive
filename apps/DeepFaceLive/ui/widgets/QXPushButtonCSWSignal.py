from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QXPushButtonCSWSignal(QCSWControl):
    def __init__(self,  csw_signal : lib_csw.Signal.Client, reflect_state_widgets=None,
                        image=None,
                        text=None, button_size=None, **kwargs):
        """
        Implements lib_csw.Signal control as QXPushButton
        """
        if not isinstance(csw_signal, lib_csw.Signal.Client):
            raise ValueError('csw_signal must be an instance of Signal.Client')

        self._csw_signal = csw_signal

        btn = self._btn = qtx.QXPushButton(image=image, text=text, released=self.on_btn_released, fixed_size=button_size)

        super().__init__(csw_control=csw_signal, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([btn]), **kwargs)

    def on_btn_released(self):
        self._csw_signal.signal()