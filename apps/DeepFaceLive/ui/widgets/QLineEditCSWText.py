from pathlib import Path

from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QLineEditCSWText(QCSWControl):
    def __init__(self, csw_text : lib_csw.Text.Client, 
                       font = None,
                       reflect_state_widgets=None):
        """
        Implements lib_csw.Text control as LineEdit
        """
        if not isinstance(csw_text, lib_csw.Text.Client):
            raise ValueError('csw_path must be an instance of Text.Client')

        self._csw_text = csw_text
        self._dlg = None

        csw_text.call_on_text(self._on_csw_text)
        
        if font is None:
            font = QXFontDB.get_default_font()
        lineedit = self._lineedit = qtx.QXLineEdit(font=font,
                                                   placeholder_text='...',
                                                   size_policy=('expanding', 'fixed'),
                                                   editingFinished=self.on_lineedit_editingFinished)

        super().__init__(csw_control=csw_text, reflect_state_widgets=reflect_state_widgets,
                         layout=qtx.QXHBoxLayout([lineedit]) )

    def _on_csw_text(self, text):

        with qtx.BlockSignals(self._lineedit):
            self._lineedit.setText(text)

    def on_lineedit_editingFinished(self):
        text = self._lineedit.text()
        if len(text) == 0:
            text = None
        self._csw_text.set_text(text)
