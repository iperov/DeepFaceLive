from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class _TextBase:
    def __init__(self):
        self._text = None
        self._on_text_evl = EventListener()

        self._call_on_msg('text', self._on_msg_text)

    def _on_msg_text(self, text):
        self._set_text(text)

    def _send_text(self):
        self._send_msg('text', self._text)

    def _set_text(self, text : str):
        if text is not None and not isinstance(text, str):
            raise ValueError('text must be str or None')

        if self._text != text:
            self._text = text
            self._on_text_evl.call(text)
            return True
        return False

    def call_on_text(self, func_or_list):
        """
        Call when the text is changed

         func(text : Union[str,None])
        """
        self._on_text_evl.add(func_or_list)

    def set_text(self, text : str):
        if self._set_text(text):
            self._send_text()

    def get_text(self): return self._text

class Text:
    """
    Text control.

    Values:
            None  : uninitialized state
            str   : value
    """
    class Host(ControlHost, _TextBase):
        def __init__(self):
            ControlHost.__init__(self)
            _TextBase.__init__(self)

        def _on_msg_text(self, text):
            if self.is_enabled():
                _TextBase._on_msg_text(self, text)
            self._send_text()

    class Client(ControlClient, _TextBase):
        def __init__(self):
            ControlClient.__init__(self)
            _TextBase.__init__(self)

        def _on_reset(self):
            self._set_text(None)
