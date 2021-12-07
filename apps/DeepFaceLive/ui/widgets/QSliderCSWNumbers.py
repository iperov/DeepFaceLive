from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QSliderCSWNumbers(QCSWControl):
    def __init__(self, csw_idx : lib_csw.Number.Client,
                       csw_idx_count : lib_csw.Number.Client,
                       ):
        """
        Implements controlable Slider with lib_csw.Number controls
        """
        if not isinstance(csw_idx, lib_csw.Number.Client):
            raise ValueError('csw_idx must be an instance of Number.Client')
        if not isinstance(csw_idx_count, lib_csw.Number.Client):
            raise ValueError('csw_idx_count must be an instance of Number.Client')

        self._csw_idx = csw_idx
        self._csw_idx_count = csw_idx_count

        csw_idx.call_on_number(self._on_csw_idx)
        csw_idx_count.call_on_number(self._on_csw_idx_count)

        slider = self._slider = qtx.QXSlider(orientation=qtx.Qt.Orientation.Horizontal,
                                             min=0,
                                             max=0,
                                             tick_position=qtx.QSlider.TickPosition.NoTicks,
                                             tick_interval=1,
                                             valueChanged=self._on_slider_valueChanged)

        spinbox_font = QXFontDB.Digital7_Mono(11, italic=True)
        spinbox_index = self._spinbox_index = qtx.QXSpinBox( font=spinbox_font, min=0, max=0, step=1, alignment=qtx.AlignRight, button_symbols=qtx.QAbstractSpinBox.ButtonSymbols.NoButtons, editingFinished=self._on_spinbox_index_editingFinished)
        spinbox_count = self._spinbox_count = qtx.QXSpinBox( font=spinbox_font, min=0, max=0, step=1, alignment=qtx.AlignRight, button_symbols=qtx.QAbstractSpinBox.ButtonSymbols.NoButtons, readonly=True)

        super().__init__(csw_control=csw_idx,
                         layout=qtx.QXVBoxLayout([slider,
                                                  (qtx.QXFrameHBox([spinbox_index, qtx.QXLabel(text='/'), spinbox_count], size_policy=('fixed', 'fixed') ) , qtx.AlignCenter),
                                                 ]) )

    def _on_csw_idx(self, idx):
        #print('_on_csw_idx', idx)
        if idx is not None:
            with qtx.BlockSignals([self._slider, self._spinbox_index]):
                self._slider.setValue(idx+1)
                self._spinbox_index.setValue(idx+1)

    def _on_csw_idx_count(self, idx_count):
        #print('_on_csw_idx_count', idx_count)
        if idx_count is not None:
            with qtx.BlockSignals([self._slider, self._spinbox_index, self._spinbox_count]):
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
