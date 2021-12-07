from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QProgressBarCSWProgress(QCSWControl):
    def __init__(self, csw_progress : lib_csw.Progress.Client):
        if not isinstance(csw_progress, lib_csw.Progress.Client):
            raise ValueError('csw_progress must be an instance of Progress.Client')

        self._csw_progress = csw_progress

        csw_progress.call_on_progress(self._on_csw_progress)
        csw_progress.call_on_config(self._on_csw_config)

        label_title = self._label_title = qtx.QXLabel('', word_wrap=True, hided=True)
        progressbar = self._progressbar = qtx.QXProgressBar( min=0, max=100, font=QXFontDB.Digital7_Mono(11, italic=True) )

        super().__init__(csw_control=csw_progress, layout=qtx.QXVBoxLayout([label_title, progressbar]) )

    def _on_csw_progress(self, progress):
        with qtx.BlockSignals(self._progressbar):
            self._progressbar.setValue(progress)

    def _on_csw_config(self, config : lib_csw.Progress.Config):
        title = config.get_title()
        if title is not None:
            self._label_title.setText(L(title))
            self._label_title.show()
        else:
            self._label_title.hide()
