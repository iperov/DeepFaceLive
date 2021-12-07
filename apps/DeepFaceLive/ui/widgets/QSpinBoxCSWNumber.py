from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QSpinBoxCSWNumber(QCSWControl):
    def __init__(self, csw_number : lib_csw.Number.Client, reflect_state_widgets=None):
        """
        Implements lib_csw.Number control as SpinBox
        """
        if not isinstance(csw_number, lib_csw.Number.Client):
            raise ValueError('csw_number must be an instance of Number.Client')

        self._csw_number = csw_number
        self._instant_update = False
        self._zero_is_auto = False
        self._read_only = True

        csw_number.call_on_number(self._on_csw_number)
        csw_number.call_on_config(self._on_csw_config)

        spinbox = self._spinbox = qtx.QXDoubleSpinBox( font=QXFontDB.Digital7_Mono(11, italic=True), min=0, max=999999999, step=1, decimals=0, readonly=self._read_only, valueChanged=self._on_spinbox_valueChanged, editingFinished=self._on_spinbox_editingFinished)
        btn_auto = self._btn_auto = qtx.QXPushButton(text=L('@misc.auto'), released=self._on_btn_auto_released, fixed_height=21, hided=True)

        super().__init__(csw_control=csw_number, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([spinbox, 1, btn_auto]) )

    def _on_csw_number(self, number):
        with qtx.BlockSignals(self._spinbox):
            self._spinbox.setValue(number)
            self._btn_auto_update()

    def _btn_auto_update(self):
        if self._zero_is_auto and self._spinbox.value() != 0:
            self._btn_auto.show()
        else:
            self._btn_auto.hide()

    def _on_csw_config(self, cfg : lib_csw.Number.Config):
        if cfg.min is not None:
            self._spinbox.setMinimum(cfg.min)
        if cfg.max is not None:
            self._spinbox.setMaximum(cfg.max)
        if cfg.step is not None:
            self._spinbox.setSingleStep(cfg.step)
        if cfg.decimals is not None:
            self._spinbox.setDecimals(cfg.decimals)

        self._zero_is_auto = cfg.zero_is_auto
        if cfg.zero_is_auto:
            self._spinbox.setSpecialValueText(L('@misc.auto'))
        else:
            self._spinbox.setSpecialValueText('')
        self._read_only = cfg.read_only
        self._spinbox.setReadOnly(cfg.read_only)
        if cfg.read_only:
            self._spinbox.setButtonSymbols(qtx.QAbstractSpinBox.ButtonSymbols.NoButtons)
        else:
            self._spinbox.setButtonSymbols(qtx.QAbstractSpinBox.ButtonSymbols.UpDownArrows)

        self._btn_auto_update()

        self._instant_update = cfg.allow_instant_update

    def _get_spinbox_value(self):
        val = self._spinbox.value()
        if self._spinbox.decimals() == 0:
            val = int(val)
        return val

    def _on_btn_auto_released(self):
        self._csw_number.set_number(0)
        #self._btn_auto_update()

    def _on_spinbox_valueChanged(self):
        if self._instant_update:
            self._csw_number.set_number(self._get_spinbox_value())

    def _on_spinbox_editingFinished(self):
        if not self._instant_update:
            self._csw_number.set_number(self._get_spinbox_value())
