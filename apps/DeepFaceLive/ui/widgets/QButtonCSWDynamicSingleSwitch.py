from typing import Union

from localization import Localization
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QButtonCSWDynamicSingleSwitch(QCSWControl):
    """
    Implements lib_csw.DynamicSingleSwitch control with radiobuttons or checkboxes
    """
    def __init__(self,  csw_switch : lib_csw.DynamicSingleSwitch.Client,
                        horizontal : bool, radio_buttons : bool):

        if not isinstance(csw_switch, lib_csw.DynamicSingleSwitch.Client):
            raise ValueError('csw_switch must be an instance of DynamicSingleSwitch.Client')

        super().__init__(csw_control=csw_switch)

        self._csw_switch = csw_switch
        self._is_radio_buttons = radio_buttons

        csw_switch.call_on_selected(self._on_csw_switch_selected)
        csw_switch.call_on_choices(self._on_csw_choices)

        self._btns = []

        main_l = self._main_l = lib_qt.QXHBoxLayout() if horizontal else lib_qt.QXVBoxLayout()

        self.setLayout(lib_qt.QXHBoxLayout([ lib_qt.QXFrame(layout=main_l, size_policy=(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed) ), ]) )
        self.hide()

    def _on_csw_choices(self, choices, choices_names, none_choice_name : Union[str,None]):
        for btn in self._btns:
            self._main_l.removeWidget(btn)
            btn.deleteLater()

        btns = self._btns = []

        for idx, choice in enumerate(choices_names):
            choice = Localization.localize(choice)
            if self._is_radio_buttons:
                btn = lib_qt.QXRadioButton(text=choice, toggled=(lambda checked, idx=idx: self.on_btns_toggled(idx, checked)) )
            else:
                btn = lib_qt.QXCheckBox(text=choice, toggled=(lambda checked, idx=idx: self.on_btns_toggled(idx, checked)) )
            btns.append(btn)
            self._main_l.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def on_btns_toggled(self, idx, checked):
        if checked:
            if not self._csw_switch.select(idx):
                with lib_qt.BlockSignals(self._btns[idx]):
                    self._btns[idx].setChecked(False)
        else:
            if not self._csw_switch.unselect():
                with lib_qt.BlockSignals(self._btns[idx]):
                    self._btns[idx].setChecked(True)

    def _on_csw_switch_selected(self, idx, choice):
        with lib_qt.BlockSignals(self._btns):
            for i,btn in enumerate(self._btns):
                btn.setChecked(i==idx)
