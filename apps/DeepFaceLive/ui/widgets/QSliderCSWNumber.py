from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QSliderCSWNumber(QCSWControl):
    def __init__(self, csw_number: lib_csw.Number.Client, reflect_state_widgets=None):
        """
        Implements lib_csw.Number control by Slider
        """
        if not isinstance(csw_number, lib_csw.Number.Client):
            raise ValueError('csw_number must be an instance of Number.Client')

        self._csw_number = csw_number

        csw_number.call_on_number(self._on_csw_number)
        csw_number.call_on_config(self._on_csw_config)

        slider = self._slider = qtx.QXSlider(orientation=qtx.Qt.Orientation.Horizontal,
                                             min=0,
                                             max=0,
                                             tick_position=qtx.QSlider.TickPosition.NoTicks,
                                             tick_interval=1,
                                             sliderReleased=self._on_slider_sliderReleased,
                                             valueChanged=self._on_slider_valueChanged)

        super().__init__(csw_control=csw_number, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXVBoxLayout([slider]))

    def _on_csw_config(self, config : lib_csw.Number.Config):
        self._config = config

        if config.min is not None and config.max is not None:
            min = config.min
            max = config.max
            step = config.step

            int_min = 0
            int_max = int( (max-min) / step )

            self._slider.setMinimum(int_min)
            self._slider.setMaximum(int_max)
            self._slider.setPageStep(1)

        self._slider.setEnabled(not config.read_only)
        self._instant_update = config.allow_instant_update

    def _on_csw_number(self, value):
        if value is not None:
            config = self._config
            value = (value-config.min) / config.step
            with qtx.BlockSignals([self._slider]):
                self._slider.setValue(value)

    def _set_csw_value(self):
        config = self._config
        value = self._slider.value()
        value = value * config.step + config.min
        self._csw_number.set_number(value)

    def _on_slider_sliderReleased(self):
        if not self._config.allow_instant_update:
            self._set_csw_value()

    def _on_slider_valueChanged(self):
        if not self._slider.isSliderDown() or self._config.allow_instant_update:
            self._set_csw_value()

