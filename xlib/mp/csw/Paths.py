from collections import Iterable
from enum import IntEnum
from pathlib import Path
from typing import List, Union

from ...python import EventListener

from .CSWBase import ControlClient, ControlHost


class _PathBase:
    def __init__(self):
        self._paths = []
        self._on_paths_evl = EventListener()
        self._call_on_msg('paths', self._on_msg_paths)

    def _on_msg_paths(self, path):
        self._set_paths(path)

    def _send_paths(self):
        self._send_msg('paths', self._paths)

    def _set_paths(self, path_or_list, block_event=False):
        if isinstance(path_or_list, Iterable) and \
            not isinstance(path_or_list, str):
            path_or_list = list(path_or_list)
        else:
            path_or_list = [path_or_list]

        for i,path in enumerate(path_or_list):
            if isinstance(path, str):
                path_or_list[i] = Path(path)
            elif not isinstance(path, Path):
                raise ValueError(f'value {path} must be an instance of str or Path')

        if self._paths != path_or_list:
            prev_paths = self._paths
            self._paths = path_or_list
            if not block_event:
                self._on_paths_evl.call(path_or_list, prev_paths)
            return True
        return False

    def call_on_paths(self, func_or_list):
        """
        Call when the path is changed

         func(path_list, prev_path_list)
        """
        self._on_paths_evl.add(func_or_list)

    def set_paths(self, path_or_list, block_event=False):
        """
        path_or_list    Path/str or list of Paths/str or []
                        or None which is same as []
        """
        if path_or_list is None:
            path_or_list = []

        if self._set_paths(path_or_list, block_event=block_event):
            self._send_paths()

    def get_paths(self): return self._paths

class Paths:
    """
    Paths control.

    Values:     []  not set
                list of [1+] Paths
    """


    class Config:
        class Type(IntEnum):
            NONE = 0
            ANY_FILE = 1
            EXISTING_FILE = 2
            EXISTING_FILES = 3
            DIRECTORY = 4

        def __init__(self, type = None, is_save = False, caption = None, suffixes = None, directory_path = None):
            if type is None:
                type = Paths.Config.Type.NONE
            self._type = type
            self._is_save = is_save
            self._caption = caption
            self._suffixes = suffixes
            self._directory_path = directory_path

        def get_type(self) -> 'Paths.Config.Type': return self._type
        def is_save(self) -> bool: return self._is_save
        def get_caption(self) -> Union[str, None]: return self._caption
        def get_suffixes(self) -> Union[List[str], None]: return self._suffixes
        def get_directory_path(self) -> Union[Path, None]: return self._directory_path

        @staticmethod
        def AnyFile(is_save=False, caption=None, suffixes=None):
            return Paths.Config(Paths.Config.Type.ANY_FILE, is_save, caption, suffixes)

        @staticmethod
        def ExistingFile(is_save=False, caption=None, suffixes=None):
            return Paths.Config(Paths.Config.Type.EXISTING_FILE, is_save, caption, suffixes)

        @staticmethod
        def ExistingFiles(caption=None, suffixes=None):
            return Paths.Config(Paths.Config.Type.EXISTING_FILES, False, caption, suffixes)

        @staticmethod
        def Directory(caption=None, directory_path=None):
            return Paths.Config(Paths.Config.Type.DIRECTORY, False, caption, None, directory_path=directory_path)


    class Host(ControlHost, _PathBase):
        def __init__(self):
            ControlHost.__init__(self)
            _PathBase.__init__(self)
            self._config = Paths.Config()

        def _on_msg_paths(self, path):
            if self.is_enabled():
                _PathBase._on_msg_paths(self, path)
            self._send_paths()

        def set_config(self, config : 'Paths.Config'):
            self._config = config
            self._send_msg('config', config)



    class Client(ControlClient, _PathBase):
        def __init__(self):
            ControlClient.__init__(self)
            _PathBase.__init__(self)
            self._on_config_evl = EventListener()
            self._call_on_msg('config', self._on_msg_config)

        def _on_msg_config(self, config : 'Paths.Config'):
            self._on_config_evl.call(config)

        def call_on_config(self, func): self._on_config_evl.add(func)

        def _on_reset(self):
            self._set_paths([])
