from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QCheckBoxCSWFlag(QCSWControl):
    """
    Implements lib_csw.Flag control as CheckBox
    """
    def __init__(self,  csw_flag : lib_csw.Flag.Client, reflect_state_widgets=None):
        if not isinstance(csw_flag, lib_csw.Flag.Client):
            raise ValueError('csw_flag must be an instance of Flag.Client')
        super().__init__(csw_control=csw_flag, reflect_state_widgets=reflect_state_widgets)
        self._csw_flag = csw_flag

        csw_flag.call_on_flag(self.on_csw_flag)
        # Init UI
        chbox = self._chbox = lib_qt.QXCheckBox(clicked=self.on_chbox_clicked)

        main_l = lib_qt.QXHBoxLayout([chbox])

        self.setLayout(main_l)
        self.hide()

    def on_csw_flag(self, flag):
        with lib_qt.BlockSignals(self._chbox):
            self._chbox.setChecked(flag)

    def on_chbox_clicked(self):
        self._csw_flag.set_flag(self._chbox.isChecked())
