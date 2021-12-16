
import threading
import time
from enum import IntEnum
from typing import Any, Callable, List, Tuple, Union
from numbers import Number
from ... import text as lib_text

class EDlgMode(IntEnum):
    UNHANDLED = 0
    BACK = 1
    RELOAD = 2
    WRONG_INPUT = 3
    HANDLED = 4



class DlgChoice:
    def __init__(self, short_name : str = None,
                       row_def : str = None,
                       on_choose : Callable = None):
        if len(short_name) == 0:
            raise ValueError('Zero len short_name is not valid.')
        self._short_name = short_name
        self._row_def = row_def
        self._on_choose = on_choose

    def get_short_name(self) -> Union[str, None]: return self._short_name
    def get_row_def(self) -> Union[str, None]: return self._row_def
    def get_on_choose(self) -> Callable: return self._on_choose

class Dlg:
    def __init__(self, on_recreate : Callable[ [], 'Dlg'] = None,
                       on_back  : Callable = None,
                       top_rows_def : Union[str, List[str]] = None,
                       bottom_rows_def : Union[str, List[str]] = None,
                       ):
        """
        base class for Diacon dialogs.
        """
        self._on_recreate = on_recreate
        self._on_back = on_back

        self._top_rows_def = top_rows_def
        self._bottom_rows_def = bottom_rows_def

    def recreate(self):
        """
        """
        if self._on_recreate is not None:
            return self._on_recreate(self)
        else:
            raise Exception('on_recreate() is not defined.')

    def set_current(self, print=True):
        Diacon.update_dlg(self, print=print)

    def handle_user_input(self, s : str):
        """
        """
        mode = self.on_user_input(s.strip())

        if mode == EDlgMode.UNHANDLED:
            mode = EDlgMode.RELOAD
        if mode == EDlgMode.WRONG_INPUT:
            print('\nWrong input')
            mode = EDlgMode.RELOAD

        if mode == EDlgMode.RELOAD:
            self.recreate().set_current()
        if mode == EDlgMode.BACK:
            if self._on_back is not None:
                self._on_back(self)

    #overridable
    def on_user_input(self, s : str) -> EDlgMode:
        if len(s) == 0:
            return EDlgMode.RELOAD
        if self._on_back is not None and len(s) == 1:
            if s == '<':
                return EDlgMode.BACK
        return EDlgMode.UNHANDLED

    def print(self, table_width_max=80, col_spacing = 3):
        """
        print dialog
        """
        table_def : List[str]= []

        trd = self._top_rows_def
        brd = self._bottom_rows_def
        if trd is not None:
            if not isinstance(trd, (list,tuple)):
                trd = [trd]
            table_def += trd

        if self._on_back is not None:
            table_def.append('| < | Go back.')

        table_def.append('|99')
        table_def = self.on_print(table_def)

        if brd is not None:
            if not isinstance(brd, (list,tuple)):
                brd = [brd]
            table_def += brd

        table = lib_text.ascii_table(table_def, max_table_width=80,
                                     left_border = '| ',
                                     right_border = ' |',
                                     border = ' | ',
                                     row_symbol = None,
                                     )
        print()
        print(table)


    #overridable
    def on_print(self, table_lines : List[Tuple[str,str]]):
        return table_lines



class DlgNumber(Dlg):
    def __init__(self, is_float : bool,
                       current_value = None,
                       min_value = None,
                       max_value = None,
                       clip_min_value = None,
                       clip_max_value = None,
                       on_value : Callable[ [Dlg, Number], None] = None,
                       on_recreate : Callable[ [], 'Dlg'] = None,
                       on_back : Callable = None,
                       top_rows_def : Union[str, List[str]] = None,
                       bottom_rows_def : Union[str, List[str]] = None, ):
        super().__init__(on_recreate=on_recreate, on_back=on_back, top_rows_def=top_rows_def, bottom_rows_def=bottom_rows_def)

        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValueError('min_value > max_value')
        if clip_min_value is not None and clip_max_value is not None and clip_min_value > clip_max_value:
            raise ValueError('clip_min_value > clip_max_value')

        self._is_float = is_float
        self._current_value = current_value
        self._min_value = min_value
        self._max_value = max_value
        self._clip_min_value = clip_min_value
        self._clip_max_value = clip_max_value
        self._on_value = on_value

    #overridable
    def on_print(self, table_def : List[str]):

        minv, maxv = self._min_value, self._max_value

        if self._is_float:
            line = '| * | Enter float number'
        else:
            line = '| * | Enter integer number'

        if minv is not None and maxv is None:
            line += f' in range: [{minv} ... )'
        elif minv is None and maxv is not None:
            line += f' in range: ( ... {maxv} ]'
        elif minv is not None and maxv is not None:
            line += f' in range: [{minv} ... {maxv} ]'

        table_def.append(line)

        return table_def

    #overridable
    def on_user_input(self, s : str) -> bool:
        result = super().on_user_input(s)
        if result == EDlgMode.UNHANDLED:
            try:
                print(s)
                v = float(s) if self._is_float else int(s)

                if self._min_value is not None:
                    if v < self._min_value:
                        return EDlgMode.WRONG_INPUT

                if self._max_value is not None:
                    if v > self._max_value:
                        return EDlgMode.WRONG_INPUT

                if self._clip_min_value is not None:
                    if v < self._clip_min_value:
                        v = self._clip_min_value

                if self._clip_max_value is not None:
                    if v > self._clip_max_value:
                        v = self._clip_max_value

                if self._on_value is not None:
                    self._on_value(self, v)
                return EDlgMode.HANDLED
            except:
                return EDlgMode.WRONG_INPUT

        return result

class DlgChoices(Dlg):
    def __init__(self, choices : List[DlgChoice],
                       on_multi_choice : Callable[ [ List[DlgChoice] ], None] = None,
                       on_recreate : Callable[ [Dlg], Dlg] = None,
                       on_back : Callable = None,
                       top_rows_def : Union[str, List[str]] = None,
                       bottom_rows_def : Union[str, List[str]] = None,
                       ):
        super().__init__(on_recreate=on_recreate, on_back=on_back, top_rows_def=top_rows_def, bottom_rows_def=bottom_rows_def)
        self._choices = choices
        self._on_multi_choice = on_multi_choice

        self._short_names = [choice.get_short_name() for choice in choices]

        # Make short names for all choices
        if len(set(self._short_names)) != len(self._short_names):
            raise ValueError(f'Contains duplicate short name : {self._short_names}')



    #overridable
    def on_print(self, table_def : List[str]):

        for short_name, choice in zip(self._short_names, self._choices):
            row_def = f'| {short_name}'
            x = choice.get_row_def()
            if x is not None:
                row_def += x
            table_def.append(row_def)

        return table_def

    #overridable
    def on_user_input(self, s : str) -> bool:
        result = super().on_user_input(s)
        if result == EDlgMode.UNHANDLED:

            if self._on_multi_choice is not None:
                multi_s = s.split(',')
            else:
                multi_s = [s]

            choices_id = []
            for s in multi_s:
                x = [ i for i, short_name in enumerate(self._short_names) if s.strip() == short_name  ]
                if len(x) == 0:
                    # No short name match
                    return EDlgMode.WRONG_INPUT
                else:
                    id = x[0]
                    choices_id.append(id)

            if len(set(choices_id)) != len(choices_id):
                # Duplicate input
                return EDlgMode.WRONG_INPUT

            for id in choices_id:
                on_choose = self._choices[id].get_on_choose()
                if on_choose is not None:
                    on_choose(self)

            if self._on_multi_choice is not None:
                self._on_multi_choice(choices_id)

            return EDlgMode.HANDLED

        return result



class _Diacon:
    """
    User dialog with via console.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._current_dlg : Dlg = None
        self._new_dlg : Dlg = None

        self._started = False
        self._dialog_t : threading.Thread = None
        self._input_t : threading.Thread = None
        self._input_request = False
        self._input_result : str = None

    def start(self):
        if self._started:
            raise Exception('Diacon already started.')
        self._started = True

        self._input_t = threading.Thread(target=self._input_thread, daemon=True)
        self._input_t.start()
        self._dialog_t = threading.Thread(target=self._dialog_thread, daemon=True)
        self._dialog_t.start()

    def stop(self):
        if not self._started:
            raise Exception('Diacon not started.')
        self._started = False
        self._dialog_t = None
        self._input_t = None

    def get_current_dlg(self) -> Union[Dlg, None]:
        return self._current_dlg

    def _input_thread(self,):
        while self._started:
            if self._input_request:
                try:
                    input_result = input()
                except Exception as e:
                    input_result = ''

                with self._lock:
                    self._input_result = input_result
                    self._input_request = False
            time.sleep(0.010)


    def _dialog_thread(self, ):
        while self._started:

            with self._lock:

                if self._new_dlg is not None:
                    (new_dlg, is_print), self._new_dlg = self._new_dlg, None
                    if new_dlg is not None:
                        self._current_dlg = new_dlg
                    if is_print:
                        self._current_dlg.print()
                    self._request_input()

                input_result = self._fetch_input()
                if input_result is not None:

                    if self._current_dlg is not None:
                        self._current_dlg.handle_user_input(input_result)
                        continue
            time.sleep(0.010)

    def _fetch_input(self):
        with self._lock:
            result = None
            if self._input_result is not None:
                result, self._input_result = self._input_result, None
            return result

    def _request_input(self):
        with self._lock:
            if not self._input_request:
                self._input_result = None
                self._input_request = True

    def update_dlg(self, new_dlg = None, print=True ):
        """
        show current or set new Dialog
        Can be called from any thread.
        """
        if not self._started:
            self.start()

        self._new_dlg = (new_dlg, print)

Diacon = _Diacon()
