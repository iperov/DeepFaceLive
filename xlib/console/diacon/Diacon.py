
import threading
import time
from enum import IntEnum
from typing import Any, Callable, List, Tuple, Union

from ... import text as lib_text

class EDlgMode(IntEnum):
    UNDEFINED = 0
    BACK = 1
    RELOAD = 2
    WRONG_INPUT = 3
    SUCCESS = 4


class DlgChoice:
    def __init__(self, name : str = None, row_desc : str = None):
        super().__init__()
        if len(name) == 0:
            raise ValueError('Zero len name is not valid.')
        self._name = name
        self._row_desc = row_desc
        
    def get_name(self) -> Union[str, None]: return self._name
    def get_row_desc(self) -> Union[str, None]: return self._row_desc
    
class Dlg:
    def __init__(self, title : str = None, has_go_back=True):
        """

        """
        self._title = title
        self._has_go_back = has_go_back

    def get_name(self) -> str: return self._name

    def handle_user_input(self, s : str) -> EDlgMode:
        """

        """
        s = s.strip()

        # ? and < available in any dialog, handle them first
        s_len = len(s)
        if s_len == 0:
            return EDlgMode.RELOAD
        if s_len == 1:
            #if s == '?':
            #    return EDlgMode.RELOAD
            if s == '<':
                return EDlgMode.BACK

        return self.on_user_input(s)

    def print(self, table_width_max=80, col_spacing = 3):
        """
        print dialog
        """
        
        # Gather table lines
        table_def : List[str]= []
        
        if self._has_go_back:
            table_def.append('| < | Go back.')
            
        table_def.append('|99')
        table_def = self.on_print(table_def)
        
        table = lib_text.ascii_table(table_def, max_table_width=80, 
                                     left_border = None,
                                     right_border = None,
                                     border = ' | ',
                                     row_symbol = None)
        print()
        print(table)
        

    #overridable
    def on_print(self, table_lines : List[Tuple[str,str]]):
        return table_lines

    #overridable
    def on_user_input(self, s : str) -> EDlgMode:
        """
        handle user input
        return False if input is invalid
        """
        return EDlgMode.UNDEFINED

class DlgChoices(Dlg):
    def __init__(self, choices : List[DlgChoice], multiple_choices=False, title : str = None, has_go_back = True):
        """

        """
        super().__init__(title=title, has_go_back=has_go_back)
        self._choices = choices
        self._multiple_choices = multiple_choices

        self._results = None
        self._results_id = None

        self._short_names = [choice.get_name() for choice in choices]

        # if any([x is not None for x in self._short_names]):
        #     # Using short names from choices
        #     if any([x is None for x in self._short_names]):
        #         raise Exception('No short name for one of choices.')
        #     if len(set(self._short_names)) != len(self._short_names):
        #         raise ValueError(f'Contains duplicate short names: {self._short_names}')
        # else:

        # Make short names for all choices
        names = [ choice.get_name() for choice in choices ]
        names_len = len(names)

        if len(set(names)) != names_len:
            raise ValueError(f'Contains duplicate name of choice : {names}')

        short_names_len = [1]*names_len
        while True:
            short_names = [ name[:short_names_len[i_name]] for i_name, name in enumerate(names) ]

            has_dup = False
            for i in range(names_len):
                i_short_name = short_names[i]

                match_count = 0
                for j in range(names_len):
                    j_short_name = short_names[j]
                    if i_short_name == j_short_name:
                        match_count += 1

                if match_count > 1:
                    has_dup = True
                    short_names_len[i] += 1

            if not has_dup:
                break
        self._short_names = short_names



    def get_selected_choices(self) -> List[DlgChoice]:
        """
        returns selected choices
        """
        return self._results

    def get_selected_choices_id(self) -> List[int]:
        """
        returns selected choice
        """
        return self._results_id

    #overridable
    def on_print(self, table_def : List[str]):
        for short_name, choice in zip(self._short_names, self._choices):
            row_def = f'| {short_name}'
            row_desc = choice.get_row_desc()
            if row_desc is not None:
                row_def += row_desc
            table_def.append(row_def)

        return table_def

    #overridable
    def on_user_input(self, s : str) -> bool:
        result = super().on_user_input(s)
        if result == EDlgMode.UNDEFINED:

            if self._multiple_choices:
                multi_s = s.split(',')
            else:
                multi_s = [s]

            results = []
            results_id = []
            for s in multi_s:
                s = s.strip()

                x = [ i for i,short_name in enumerate(self._short_names) if s == short_name  ]
                if len(x) == 0:
                    # no short name match
                    return EDlgMode.WRONG_INPUT
                else:
                    id = x[0]
                    results_id.append(id)
                    results.append(self._choices[id])

            if len(set(results_id)) != len(results_id):
                # Duplicate input
                return EDlgMode.WRONG_INPUT

            self._results = results
            self._results_id = results_id

            return EDlgMode.SUCCESS

        return result



class _Diacon:
    """
    User dialog with via console.

    Internal architecture:

    [
        Main-Thread

        current thread from which __init__() called
    ]

    [
        Dialog-Thread

        separate thread where dialogs are handled and dynamically created

        we need this thread, because main thread can be busy,
        for example training neural network

        calls on_dlg() provided with __init__

        thus keep in mind on_dlg() works in separate thread

        This thread must not be blocked inside on_dlg(),
        because Diacon.stop() can be called that stops all threads.
    ]

    [
        Input-Thread

        separate thread where user input is accepted in non-blocking mode,
        and transfered to processing thread
    ]
    """

    def __init__(self):
        self._on_dlg : Callable = None

        self._lock = threading.RLock()
        self._current_dlg : Dlg = None
        self._new_dlg : Dlg = None

        self._started = False
        self._dialog_t : threading.Thread = None
        self._input_t : threading.Thread = None
        self._input_request = False
        self._input_result : str = None

    def start(self, on_dlg : Callable):
        if self._started:
            raise Exception('Diacon already started.')
        self._started = True
        self._on_dlg = on_dlg

        self._input_t = threading.Thread(target=self._input_thread, daemon=True)
        self._input_t.start()
        self._dialog_t = threading.Thread(target=self._dialog_thread, daemon=True)
        self._dialog_t.start()

    def stop(self):
        if not self._started:
            raise Exception('Diacon not started.')
        self._started = False
        self._dialog_t.join()
        self._dialog_t = None
        self._input_t.join()
        self._input_t = None

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
                time.sleep(0.050)


    def _dialog_thread(self, ):
        self._on_dlg(None, EDlgMode.RELOAD)

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
                        mode = self._current_dlg.handle_user_input(input_result)
                        if mode == EDlgMode.WRONG_INPUT:
                            print('\nWrong input')
                            mode = EDlgMode.RELOAD
                        if mode == EDlgMode.UNDEFINED:
                            mode = EDlgMode.RELOAD
                        self._on_dlg(self._current_dlg, mode)
                        continue

            time.sleep(0.005)

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
        self._new_dlg = (new_dlg, print)

Diacon = _Diacon()
