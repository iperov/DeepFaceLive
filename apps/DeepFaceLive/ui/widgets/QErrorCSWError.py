from typing import Union

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl

        
        
class QErrorCSWError(QCSWControl):
    """
    Implements lib_csw.Error control as widget
    """
    def __init__(self,  csw_error : lib_csw.Error.Client):
        if not isinstance(csw_error, lib_csw.Error.Client):
            raise ValueError('csw_error must be an instance of Error.Client')
        super().__init__(csw_control=csw_error)
        self._csw_error = csw_error
        csw_error.call_on_error(self._on_csw_error)

        label_warning = self._label_warning = lib_qt.QXLabel(image=QXImageDB.warning_outline('red'),
                                                             scaled_contents=True,
                                                             size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
                                                             fixed_size=(32,32),
                                                              )

        label = self._label = lib_qt.QXTextEdit( font=QXFontDB.get_default_font(size=7), read_only=True, fixed_height=80 )

        bar = lib_qt.QXFrame(layout=lib_qt.QXHBoxLayout(
                                [   lib_qt.QXWidget(layout=lib_qt.QXHBoxLayout([label_warning]), size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)) ,
                                    lib_qt.QXWidget(layout=lib_qt.QXHBoxLayout([label]))
                                ], spacing=0) )

        self.setLayout(lib_qt.QXHBoxLayout([bar]))
        self.hide()

    def _on_csw_state_change(self, state):
        super()._on_csw_state_change(state)
        if state == lib_csw.Control.State.DISABLED:
            self._label.setText(None)

    def _on_csw_error(self, text: Union[str,None]):
        self._label.setText(text)
