from typing import Union

from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QComboBoxCSWDynamicSingleSwitch(QCSWControl):
    """
    Implements lib_csw.DynamicSingleSwitch control with QComboBox
    """
    def __init__(self,  csw_switch : lib_csw.DynamicSingleSwitch.Client, reflect_state_widgets=None):
        if not isinstance(csw_switch, lib_csw.DynamicSingleSwitch.Client):
            raise ValueError('csw_switch must be an instance of DynamicSingleSwitch.Client')
        self._csw_switch = csw_switch
        self._has_none_choice = True

        csw_switch.call_on_selected(self._on_csw_switch_selected)
        csw_switch.call_on_choices(self._on_csw_choices)

        self._combobox = None
        self._main_l = qtx.QXHBoxLayout()
        super().__init__(csw_control=csw_switch, reflect_state_widgets=reflect_state_widgets, layout=self._main_l)

    def _on_csw_choices(self, choices, choices_names, none_choice_name : Union[str,None]):
        idx = 0
        if self._combobox is not None:
            idx = self._combobox.currentIndex()
            self._main_l.removeWidget(self._combobox)
            self._combobox.deleteLater()

        self._choices_names = choices_names
        self._has_none_choice = none_choice_name is not None

        combobox = self._combobox = qtx.QXComboBox(font=QXFontDB.get_fixedwidth_font(), on_index_changed=self.on_combobox_index_changed)
        with qtx.BlockSignals(self._combobox):
            if none_choice_name is not None:
                combobox.addItem( qtx.QIcon(), L(none_choice_name) )

            for choice_name in choices_names:
                combobox.addItem( qtx.QIcon(), L(choice_name) )
        
            combobox.setCurrentIndex(idx)
        
        self._main_l.addWidget(combobox)

    def on_combobox_index_changed(self, idx):
        if self._has_none_choice and idx == 0:
            self._csw_switch.unselect()
        else:
            if self._has_none_choice:
                idx -= 1

            if not self._csw_switch.select(idx):
                raise Exception('error on select')

    def _on_csw_switch_selected(self, idx, choice):
        with qtx.BlockSignals(self._combobox):
            if idx is None:
                self._combobox.setCurrentIndex(0)
            else:
                if self._has_none_choice:
                    idx += 1

                self._combobox.setCurrentIndex(idx)
