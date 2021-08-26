from typing import Union

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class Error:
    """
    One-way error control.

    """

    class Client(ControlClient):
        def __init__(self):
            ControlClient.__init__(self)

            self._on_error_evl = EventListener()
            self._call_on_msg('error', self._on_msg_error)

        def _on_msg_error(self, text):
            self._on_error_evl.call(text)

        def call_on_error(self, func_or_list):
            """
            Call when the error message arrive

             func(text : Union[str,None])
            """
            self._on_error_evl.add(func_or_list)

        def _on_reset(self):
            self._on_msg_error(None)


    class Host(ControlHost):
        def __init__(self):
            ControlHost.__init__(self)


        def set_error(self, text : Union[str, None]):
            """
            set tex

             text   str or None
            """
            if text is None:
                self.disable()
            else:
                self.enable()
                self._send_msg('error', text)


