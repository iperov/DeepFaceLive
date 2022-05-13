from collections import Iterable
from typing import List, Union

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class _DynamicSingleSwitchBase:
    def __init__(self):
        self._on_selected_evl = EventListener()
        self._on_choices_evl = EventListener()

        self._call_on_msg('selected_idx', self._on_msg_selected)
        self._call_on_msg('choices', self._on_msg_choices)

        self._selected_idx = None

        self._choices = None
        self._choices_len = None
        self._choices_names = None
        self._none_choice_name = None

    def _on_msg_selected(self, selected_idx):
        self._set_selected_idx(selected_idx)

    def _send_selected_idx(self):
        self._send_msg('selected_idx', self.get_selected_idx() )

    def _set_selected_idx(self, selected_idx):
        if self._selected_idx != selected_idx:
            self._selected_idx = selected_idx
            self._on_selected_evl.call(selected_idx, self.get_selected_choice() )
            return True
        return False

    def _send_choices(self):
        self._send_msg('choices', self._choices, self._choices_names, self._none_choice_name)

    def _set_choices(self, choices, choices_names : List[str], none_choice_name : Union[str,None]):
        self._choices = choices
        self._choices_len = len(choices)
        self._choices_names = choices_names
        self._none_choice_name = none_choice_name
        self._on_choices_evl.call(choices, choices_names, none_choice_name)

    def _on_msg_choices(self, choices, choices_names, none_choice_name):
        self._set_choices(choices, choices_names, none_choice_name)

    def _choice_to_index(self, idx_or_choice):
        choices = self._choices
        if idx_or_choice.__class__ != int:
            try:
                idx_or_choice = choices.index(idx_or_choice)
            except:
                # Choice not in list
                return None
        if idx_or_choice < 0 or idx_or_choice >= self._choices_len:
            # idx out of bounds
            return None
        return idx_or_choice

    def call_on_choices(self, func_or_list):
        """call when choices list is configured"""
        self._on_choices_evl.add(func_or_list)

    def call_on_selected(self, func):
        """
        called when selected
         func ( idx : int, choice : object)
        """
        self._on_selected_evl.add(func)

    def in_choices(self, choice) -> bool: return choice in self._choices

    def get_choices(self): return self._choices
    def get_choices_names(self) -> List[str]: return self._choices_names

    def get_selected_idx(self) -> Union[int, None]: return self._selected_idx
    def get_selected_choice(self):
        if self._selected_idx is None:
            return None
        return self._choices[self._selected_idx]

    def select(self, idx_or_choice) -> bool:
        """
        Select index or choice or None(unselect)

        returns False if the value is not correct or already selected
        returns True if operation is success

        func does not raise any exceptions
        """
        if idx_or_choice is not None:
            idx_or_choice = self._choice_to_index (idx_or_choice)
            if idx_or_choice is None:
                return False

        result = self._set_selected_idx(idx_or_choice)
        if result:
            self._send_selected_idx()
        return result

    def unselect(self) -> bool:
        """
        unselect
        returns True if operation is success
        """
        return self.select(None)


class DynamicSingleSwitch:
    """
    DynamicSingleSwitch control dynamically loaded list of choices.
    Has None state as unselected.


    """
    class Host(ControlHost, _DynamicSingleSwitchBase):
        def __init__(self):
            ControlHost.__init__(self)
            _DynamicSingleSwitchBase.__init__(self)

        def _on_msg_selected(self, selected_idx):
            if self.is_enabled():
                _DynamicSingleSwitchBase._on_msg_selected(self, selected_idx)
            self._send_selected_idx()

        def set_choices(self, choices, choices_names=None, none_choice_name=None):
            """
            set choices, and optional choices_names.

             choices_names  list/dict/None  if list, should match the len of choices
                                            if dict, should return a str by key of choice
                                            if None, choices will be stringfied

             none_choice_name('')   str/None  if not None, shows None choice with name,
                                                by default empty string
            """
            self.unselect()

            # Validate choices
            if choices is None:
                raise ValueError('Choices cannot be None.')
            if not isinstance(choices, Iterable):
                raise ValueError('Choices must be Iterable')

            if choices_names is None:
                choices_names = tuple(str(c) for c in choices)
            elif isinstance(choices_names, (list,tuple)):
                if len(choices_names) != len(choices):
                    raise ValueError('mismatch len of choices and choices names')
            elif isinstance(choices_names, dict):
                choices_names = [ choices_names[x] for x in choices ]
            else:
                raise ValueError('unsupported type of choices_names')

            if not all( isinstance(x, str) for x in choices_names ):
                raise ValueError('all values in choices_names must be a str')

            choices = tuple(choices)

            self._set_choices(choices, choices_names, none_choice_name)
            self._send_choices()

    class Client(ControlClient, _DynamicSingleSwitchBase):
        def __init__(self):
            ControlClient.__init__(self)
            _DynamicSingleSwitchBase.__init__(self)

        def _on_reset(self):
            self._set_selected_idx(None)


