from typing import Union

from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QErrorCSWError(QCSWControl):
    """
    Implements lib_csw.Error control as widget
    """
    def __init__(self,  csw_error : lib_csw.Error.Client):
        if not isinstance(csw_error, lib_csw.Error.Client):
            raise ValueError('csw_error must be an instance of Error.Client')

        self._csw_error = csw_error
        csw_error.call_on_error(self._on_csw_error)

        self._label_warning = qtx.QXLabel(image=QXImageDB.warning_outline('red'),
                                          scaled_contents=True,
                                          size_policy=('fixed', 'fixed'),
                                          fixed_size=(32,32) )

        self._label = qtx.QXTextEdit( font=QXFontDB.get_default_font(size=7), read_only=True, fixed_height=80)

        super().__init__(csw_control=csw_error,
                         layout=qtx.QXHBoxLayout([self._label_warning, self._label]) )

    def _on_csw_state_change(self, state):
        super()._on_csw_state_change(state)
        if state == lib_csw.Control.State.DISABLED:
            self._label.setText(None)

    def _on_csw_error(self, text: Union[str,None]):
        self._label.setText(text)
