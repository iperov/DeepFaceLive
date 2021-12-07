from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QCheckBoxCSWFlag(QCSWControl):
    """
    Implements lib_csw.Flag control as CheckBox
    """
    def __init__(self,  csw_flag : lib_csw.Flag.Client, reflect_state_widgets=None):
        if not isinstance(csw_flag, lib_csw.Flag.Client):
            raise ValueError('csw_flag must be an instance of Flag.Client')
            
        self._csw_flag = csw_flag
        csw_flag.call_on_flag(self.on_csw_flag)
        
        chbox = self._chbox = qtx.QXCheckBox(clicked=self.on_chbox_clicked)
        
        super().__init__(csw_control=csw_flag, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([chbox]))

    def on_csw_flag(self, flag):
        with qtx.BlockSignals(self._chbox):
            self._chbox.setChecked(flag)

    def on_chbox_clicked(self):
        self._csw_flag.set_flag(self._chbox.isChecked())
