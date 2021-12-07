from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QLabelCSWNumber(QCSWControl):
    """
    Implements lib_csw.Number control as QXLabel read-only
    """
    def __init__(self, csw_number : lib_csw.Number.Client, reflect_state_widgets=None):

        if not isinstance(csw_number, lib_csw.Number.Client):
            raise ValueError('csw_number must be an instance of Number.Client')

        self._csw_number = csw_number
        self._decimals = 0

        csw_number.call_on_number(self._on_csw_number)
        csw_number.call_on_config(self._on_csw_config)

        label = self._label = qtx.QXLabel( font=QXFontDB.Digital7_Mono(11, italic=True) )

        super().__init__(csw_control=csw_number, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([label]))

    def _on_csw_number(self, number):
        f = (10**self._decimals)
        number = int(number * f) / f
        self._label.setText(str(number))

    def _on_csw_config(self, cfg : lib_csw.Number.Config):
        if not cfg.read_only:
            raise Exception('QLabelCSWNumber supports only read-only Number')

        if cfg.decimals is not None:
            self._decimals = cfg.decimals

