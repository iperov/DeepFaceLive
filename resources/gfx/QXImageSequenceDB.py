from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from xlib import path as lib_path
from xlib.qt.gui.from_file import QXImage_from_file
from xlib.qt.gui.QXImageSequence import QXImageSequence


class QXImageSequenceDB:
    cached = {}

    def _get(dir_path : Path, fps, color=None):
        key = (dir_path, fps, color)
        result = QXImageSequenceDB.cached.get(key, None)
        if result is None:
            image_paths = lib_path.get_files_paths(dir_path)
            result = QXImageSequenceDB.cached[key] = QXImageSequence(frames=[QXImage_from_file (image_path, color) for image_path in image_paths], fps=fps)
        return result

    def icon_loading(color=None) -> QXImageSequence: return QXImageSequenceDB._get(Path(__file__).parent / 'sequences' / 'icon_loading', fps=30, color=color)
