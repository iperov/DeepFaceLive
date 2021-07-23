from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QSliderCSWNumbers(QCSWControl):
    """
    Implements controlable Slider with lib_csw.Number controls
    """
    def __init__(self, csw_idx : lib_csw.Number.Client,
                       csw_idx_count : lib_csw.Number.Client,
                       ):

        if not isinstance(csw_idx, lib_csw.Number.Client):
            raise ValueError('csw_idx must be an instance of Number.Client')
        if not isinstance(csw_idx_count, lib_csw.Number.Client):
            raise ValueError('csw_idx_count must be an instance of Number.Client')

        super().__init__(csw_control=csw_idx)

        self._csw_idx = csw_idx
        self._csw_idx_count = csw_idx_count

        csw_idx.call_on_number(self._on_csw_idx)
        csw_idx_count.call_on_number(self._on_csw_idx_count)
        # Init UI
        slider = self._slider = lib_qt.QXSlider(orientation=Qt.Orientation.Horizontal,
                                                min=0,
                                                max=0,
                                                tick_position=QSlider.TickPosition.NoTicks,
                                                tick_interval=1,
                                                valueChanged=self._on_slider_valueChanged)

        spinbox_font = QXFontDB.Digital7_Mono(11, italic=True)
        spinbox_index = self._spinbox_index = lib_qt.QXSpinBox( font=spinbox_font, min=0, max=0, step=1, alignment=Qt.AlignmentFlag.AlignRight, button_symbols=QAbstractSpinBox.ButtonSymbols.NoButtons, editingFinished=self._on_spinbox_index_editingFinished)
        spinbox_count = self._spinbox_count = lib_qt.QXSpinBox( font=spinbox_font, min=0, max=0, step=1, alignment=Qt.AlignmentFlag.AlignRight, button_symbols=QAbstractSpinBox.ButtonSymbols.NoButtons, readonly=True)

        main_l = lib_qt.QXVBoxLayout([
                        slider,
                        lib_qt.QXHBoxLayout([lib_qt.QXFrame(layout=lib_qt.QXHBoxLayout([spinbox_index, lib_qt.QXLabel(text='/', ), spinbox_count]),
                                              size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) )])
                        ])

        self.setLayout(main_l)
        self.hide()

    def _on_csw_idx(self, idx):
        #print('_on_csw_idx', idx)
        if idx is not None:
            with lib_qt.BlockSignals([self._slider, self._spinbox_index]):
                self._slider.setValue(idx+1)
                self._spinbox_index.setValue(idx+1)

    def _on_csw_idx_count(self, idx_count):
        #print('_on_csw_idx_count', idx_count)
        if idx_count is not None:
            with lib_qt.BlockSignals([self._slider, self._spinbox_index, self._spinbox_count]):
                self._slider.setMinimum(1)
                self._slider.setMaximum(idx_count)
                self._spinbox_index.setMinimum(1)
                self._spinbox_index.setMaximum(idx_count)
                self._spinbox_count.setMaximum(idx_count)
                self._spinbox_count.setValue(idx_count)

    def _on_slider_valueChanged(self):
        self._csw_idx.set_number(self._slider.value()-1)

    def _on_spinbox_index_editingFinished(self):
        self._csw_idx.set_number(self._spinbox_index.value()-1)
