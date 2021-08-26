from ...python import EventListener

from .CSWBase import ControlClient, ControlHost

class Signal:
    class Host(ControlHost):
        def __init__(self):
            super().__init__()

            self._signal_evl = EventListener()
            self._call_on_msg('signal', self._on_msg_signal)

        def call_on_signal(self, func): self._signal_evl.add(func)

        def signal(self):
            self._on_msg_signal()

        def _on_msg_signal(self):
            if self.is_enabled():
                self._signal_evl.call()

    class Client(ControlClient):
        def signal(self):
            self._send_msg('signal')

        def _on_reset(self):
            ...
