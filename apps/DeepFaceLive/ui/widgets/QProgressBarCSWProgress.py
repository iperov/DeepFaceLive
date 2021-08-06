from localization import L
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl


class QProgressBarCSWProgress(QCSWControl):
    """
    """
    def __init__(self, csw_progress : lib_csw.Progress.Client):

        if not isinstance(csw_progress, lib_csw.Progress.Client):
            raise ValueError('csw_progress must be an instance of Progress.Client')
        super().__init__(csw_control=csw_progress)

        self._csw_progress = csw_progress

        csw_progress.call_on_progress(self._on_csw_progress)
        csw_progress.call_on_config(self._on_csw_config)

        label_title = self._label_title = lib_qt.QXLabel('', word_wrap=True, hided=True)
        progressbar = self._progressbar = lib_qt.QXProgressBar( min=0, max=100, font=QXFontDB.Digital7_Mono(11, italic=True) ) # ,, step=1, decimals=0, readonly=self._read_only, valueChanged=self._on_spinbox_valueChanged, editingFinished=self._on_spinbox_editingFinished)

        self.setLayout( lib_qt.QXVBoxLayout([label_title, progressbar]) )
        self.hide()

    def _on_csw_progress(self, progress):
        with lib_qt.BlockSignals(self._progressbar):
            self._progressbar.setValue(progress)


    def _on_csw_config(self, config : lib_csw.Progress.Config):
        title = config.get_title()
        if title is not None:
            self._label_title.setText(L(title))
            self._label_title.show()
        else:
            self._label_title.hide()
