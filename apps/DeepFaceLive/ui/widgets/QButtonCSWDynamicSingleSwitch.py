from typing import Union

from localization import Localization
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QButtonCSWDynamicSingleSwitch(QCSWControl):
    def __init__(self,  csw_switch : lib_csw.DynamicSingleSwitch.Client,
                        horizontal : bool, radio_buttons : bool):
        """
        Implements lib_csw.DynamicSingleSwitch control with radiobuttons or checkboxes
        """
        if not isinstance(csw_switch, lib_csw.DynamicSingleSwitch.Client):
            raise ValueError('csw_switch must be an instance of DynamicSingleSwitch.Client')

        self._csw_switch = csw_switch
        self._is_radio_buttons = radio_buttons

        csw_switch.call_on_selected(self._on_csw_switch_selected)
        csw_switch.call_on_choices(self._on_csw_choices)

        self._btns = []
        self._main_l = qtx.QXHBoxLayout() if horizontal else qtx.QXVBoxLayout()
        super().__init__(csw_control=csw_switch, layout=self._main_l)

    def _on_csw_choices(self, choices, choices_names, none_choice_name : Union[str,None]):
        for btn in self._btns:
            self._main_l.removeWidget(btn)
            btn.deleteLater()

        btns = self._btns = []

        for idx, choice in enumerate(choices_names):
            choice = Localization.localize(choice)
            if self._is_radio_buttons:
                btn = qtx.QXRadioButton(text=choice, toggled=(lambda checked, idx=idx: self.on_btns_toggled(idx, checked)) )
            else:
                btn = qtx.QXCheckBox(text=choice, toggled=(lambda checked, idx=idx: self.on_btns_toggled(idx, checked)) )
            btns.append(btn)
            self._main_l.addWidget(btn, alignment=qtx.AlignCenter)

    def on_btns_toggled(self, idx, checked):
        if checked:
            if not self._csw_switch.select(idx):
                with qtx.BlockSignals(self._btns[idx]):
                    self._btns[idx].setChecked(False)
        else:
            if not self._csw_switch.unselect():
                with qtx.BlockSignals(self._btns[idx]):
                    self._btns[idx].setChecked(True)

    def _on_csw_switch_selected(self, idx, choice):
        with qtx.BlockSignals(self._btns):
            for i,btn in enumerate(self._btns):
                btn.setChecked(i==idx)
