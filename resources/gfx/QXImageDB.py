from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from xlib.qt.gui.from_file import QXImage_from_file


class QXImageDB:
    cached = {}

    def _get(filename : str, color=None):

        if isinstance(color, QColor):
            key = (filename, color.getRgb() )
        else:
            key = (filename, color)
        result = QXImageDB.cached.get(key, None)
        if result is None:
            result = QXImageDB.cached[key] = QXImage_from_file ( Path(__file__).parent / 'images' / filename, color )
        return result


    def add_circle_outline(color='black'): return QXImageDB._get('add-circle-outline.png', color)
    def close_outline(color='black'): return QXImageDB._get('close-outline.png', color)

    def eye_outline(color='black'): return QXImageDB._get('eye-outline.png', color)

    def folder_open_outline(color='black'): return QXImageDB._get('folder-open-outline.png', color)
    def open_outline(color='black'): return QXImageDB._get('open-outline.png', color)
    def information_circle_outline(color='black'): return QXImageDB._get('information-circle-outline.png', color)


    def play_circle_outline(color='black'): return QXImageDB._get('play-circle-outline.png', color)
    def play_back_circle_outline(color='black'): return QXImageDB._get('play-back-circle-outline.png', color)
    def play_forward_circle_outline(color='black'): return QXImageDB._get('play-forward-circle-outline.png', color)
    def play_skip_back_circle_outline(color='black'): return QXImageDB._get('play-skip-back-circle-outline.png', color)
    def play_skip_forward_circle_outline(color='black'): return QXImageDB._get('play-skip-forward-circle-outline.png', color)

    def pause_circle_outline(color='black'): return QXImageDB._get('pause-circle-outline.png', color)
    def power_outline(color='black'): return QXImageDB._get('power-outline.png', color)
    def reload_outline(color='black'): return QXImageDB._get('reload-outline.png', color)
    def settings_outline(color='black'): return QXImageDB._get('settings-outline.png', color)
    def settings_reset_outline(color='black'): return QXImageDB._get('settings-reset-outline.png', color)

    def warning_outline(color='black'): return QXImageDB._get('warning-outline.png', color)

    def app_icon(): return QXImageDB._get('app_icon.png', None)
    def logo_barclay_stone(): return QXImageDB._get('logo_barclay_stone.png', None)
    def logo_exmo(): return QXImageDB._get('logo_exmo.png', None)
    def splash_deepfacelive(): return QXImageDB._get('splash_deepfacelive.png', None)
