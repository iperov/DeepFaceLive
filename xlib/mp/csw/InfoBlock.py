from typing import Union, List

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class InfoBlock:
    """

    """

    class Client(ControlClient):
        def __init__(self):
            ControlClient.__init__(self)

            self._on_info_evl = EventListener()
            self._call_on_msg('info', self._on_msg_info)

        def _on_msg_info(self, lines):
            self._on_info_evl.call(lines)

        def call_on_info(self, func_or_list):
            """
            Call when the error message arrive

             func( lines : Union[ List[str], None] )
            """
            self._on_info_evl.add(func_or_list)

        def _on_reset(self):
            self._on_msg_info(None)


    class Host(ControlHost):
        def __init__(self):
            ControlHost.__init__(self)


        def set_info(self, lines : Union[ List[str], None]):
            """
            set info

                lines   List[str] | None
            """
            self._send_msg('info', lines)


