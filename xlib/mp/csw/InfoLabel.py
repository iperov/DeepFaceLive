from typing import Union, List

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class InfoLabel:
    """

    """
    class Config:
        def __init__(self, label : Union[str, None] = None,
                           info_icon = False,
                           info_lines : Union[ List[str], None] = None):
            self.label = label
            self.info_icon = info_icon
            self.info_lines = info_lines

    class Client(ControlClient):
        def __init__(self):
            ControlClient.__init__(self)

            self._on_config_evl = EventListener()
            self._call_on_msg('_cfg', self._on_msg_config)

        def _on_msg_config(self, cfg):
            self._on_config_evl.call(cfg)

        def call_on_config(self, func_or_list):
            """
            """
            self._on_config_evl.add(func_or_list)

        def _on_reset(self):
            ...
        #    self._on_msg_config( InfoLabel.Config() )


    class Host(ControlHost):
        def __init__(self):
            ControlHost.__init__(self)

        def set_config(self, cfg : 'InfoLabel.Config'):
            """
            """
            self._send_msg('_cfg', cfg)

