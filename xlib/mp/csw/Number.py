import numpy as np
from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class _NumberBase:
    def __init__(self):
        self._number = None
        self._on_number_evl = EventListener()
        self._call_on_msg('number', self._on_msg_number)

    def _on_msg_number(self, number):
        self._set_number(number)

    def _send_number(self):
        self._send_msg('number', self._number)

    def _set_number(self, number, block_event=False):
        if number is not None:
            if isinstance(number, (int, np.int, np.int8, np.int16, np.int32, np.int64)):
                number = int(number)
            elif isinstance(number, (float, np.float, np.float16, np.float32, np.float64)):
                number = float(number)
            else:
                raise ValueError('number must be an instance of int/float')

        if self._number != number:
            self._number = number
            if not block_event:
                self._on_number_evl.call(number if number is not None else 0)
            return True
        return False

    def call_on_number(self, func_or_list):
        """Call when the number is changed."""
        self._on_number_evl.add(func_or_list)

    def set_number(self, number, block_event=False):
        """

         block_event(False)     bool  on_number event will not be called on this side
        """
        if self._set_number(number, block_event=block_event):
            self._send_number()

    def get_number(self): return self._number

class Number:
    """
    Number control.

    Values:
            None        : uninitialized state
            int/float   : value
    """

    class Config:
        """
            allow_instant_update    mean that the user widget can
                                    send the value immediatelly during change,
                                    for example - scrolling the spinbox

        """

        def __init__(self, min=None, max=None, step=None, decimals=None, zero_is_auto : bool =False, allow_instant_update : bool =False, read_only : bool =False):
            self.min = min
            self.max = max
            self.step = step
            self.decimals = decimals
            self.zero_is_auto : bool = zero_is_auto
            self.allow_instant_update : bool = allow_instant_update
            self.read_only : bool = read_only


    class Host(ControlHost, _NumberBase):
        def __init__(self):
            ControlHost.__init__(self)
            _NumberBase.__init__(self)
            self._config = Number.Config()

        def _on_msg_number(self, number):
            if self.is_enabled():
                _NumberBase._on_msg_number(self, number)
            self._send_number()

        def get_config(self) -> 'Number.Config':
            return self._config

        def set_config(self, config : 'Number.Config'):
            self._config = config
            self._send_msg('config', config)

    class Client(ControlClient, _NumberBase):
        def __init__(self):
            ControlClient.__init__(self)
            _NumberBase.__init__(self)
            self._on_config_evl = EventListener()
            self._call_on_msg('config', self._on_msg_config)

        def _on_reset(self):
            self._set_number(None)

        def _on_msg_config(self, cfg : 'Number.Config'):
            self._on_config_evl.call(cfg)

        def call_on_config(self, func): self._on_config_evl.add(func)
