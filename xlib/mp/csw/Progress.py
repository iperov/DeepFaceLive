from typing import Union

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class _ProgressBase:
    def __init__(self):
        self._progress = None
        self._on_progress_evl = EventListener()
        self._call_on_msg('progress', self._on_msg_progress)

    def _on_msg_progress(self, progress):
        self._set_progress(progress)

    def _set_progress(self, progress, block_event=False):
        if progress is not None:
            progress = int(progress)

        if self._progress != progress:
            self._progress = progress
            if not block_event:
                self._on_progress_evl.call(progress if progress is not None else 0)
            return True
        return False

    def call_on_progress(self, func_or_list):
        """Call when the progress is changed."""
        self._on_progress_evl.add(func_or_list)

    def get_progress(self): return self._progress

class Progress:
    """
    Progress control with 0..100 int value

    Values:
            None        : uninitialized state
            int/float   : value
    """

    class Config:
        def __init__(self, title=None):
            self._title = title

        def get_title(self) -> Union[str, None]:
            return self._title

    class Host(ControlHost, _ProgressBase):
        def __init__(self):
            ControlHost.__init__(self)
            _ProgressBase.__init__(self)
            self._config = Progress.Config()

        def _send_progress(self):
            self._send_msg('progress', self._progress)

        def set_progress(self, progress, block_event=False):
            """
             progress   number      0..100
             block_event(False)     on_progress event will not be called on this side
            """
            if self._set_progress(progress, block_event=block_event):
                self._send_progress()

        def set_config(self, config : 'Progress.Config'):
            self._send_msg('config', config)

    class Client(ControlClient, _ProgressBase):
        def __init__(self):
            ControlClient.__init__(self)
            _ProgressBase.__init__(self)
            self._on_config_evl = EventListener()
            self._call_on_msg('config', self._on_msg_config)

        def _on_reset(self):
            self._set_progress(None)

        def _on_msg_config(self, config):
            self._on_config_evl.call(config)

        def call_on_config(self, func):
            self._on_config_evl.add(func)
