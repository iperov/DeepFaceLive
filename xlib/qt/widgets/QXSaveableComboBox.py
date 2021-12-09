from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from typing import Iterable
from .QXComboBox import QXComboBox
from .QXMainApplication import QXMainApplication
from ..core.widget import BlockSignals

class QXSaveableComboBox(QXComboBox):
    
    def __init__(self, db_key, choices : Iterable, default_choice, choices_names=None, on_choice_selected = None):
        """
        a saveable QXComboBox
        """
        self._choices = [x for x in choices]
        self._default_choice = default_choice

        if choices_names is None:
            choices_names = [str(x) for x in choices]
        self._choices_names = choices_names

        if len(self._choices) != len(self._choices_names):
            raise ValueError('mismatch len of choices and choices_names')

        self._db_key = db_key
        self._on_choice_selected = on_choice_selected

        super().__init__(choices=choices_names, on_index_changed=self._index_changed)

        self.set_choice( QXMainApplication.inst.get_app_data (db_key) )

    def set_choice(self, choice):
        if choice not in self._choices:
            choice = self._default_choice

        QXMainApplication.inst.set_app_data(self._db_key, choice)

        idx = self._choices.index(choice)

        if self._on_choice_selected is not None:
            self._on_choice_selected(self._choices[idx], self._choices_names[idx])

        with BlockSignals(self):
            self.setCurrentIndex(idx)

    def _index_changed(self, idx):
        self.set_choice( self._choices[idx] )