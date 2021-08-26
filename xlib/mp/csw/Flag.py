from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class _FlagBase:
    def __init__(self):
        self._flag = None
        self._on_flag_evl = EventListener()

        self._call_on_msg('flag', self._on_msg_flag)

    def _on_msg_flag(self, flag):
        self._set_flag(flag)

    def _send_flag(self):
        self._send_msg('flag', self._flag)

    def _set_flag(self, flag : bool):
        if flag is not None and not isinstance(flag, bool):
            raise ValueError('flag must be a bool value or None')

        if self._flag != flag:
            self._flag = flag
            self._on_flag_evl.call(flag if flag is not None else False)
            return True
        return False

    def call_on_flag(self, func):
        """Call when the flag is changed"""
        self._on_flag_evl.add(func)

    def set_flag(self, flag : bool):
        if self._set_flag(flag):
            self._send_flag()

    def get_flag(self): return self._flag

class Flag:
    """
    Flag control.

    Values:  None   : uninitialized/not set
             bool   : value
    """
    class Host(ControlHost, _FlagBase):
        def __init__(self):
            ControlHost.__init__(self)
            _FlagBase.__init__(self)

        def _on_msg_flag(self, flag):
            if self.is_enabled():
                _FlagBase._on_msg_flag(self, flag)
            self._send_flag()

    class Client(ControlClient, _FlagBase):
        def __init__(self):
            ControlClient.__init__(self)
            _FlagBase.__init__(self)

        def _on_reset(self):
            self._set_flag(None)
