from pathlib import Path

from localization import Localization
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from xlib import path as lib_path


class QXFontDB():
    _cached = {}

    _file_to_family = {}

    _families_loaded = set()

    @staticmethod
    def _load_family(name : str):
        if name in QXFontDB._families_loaded:
            return
        QXFontDB._families_loaded.add(name)

        dir = Path(__file__).parent / name
        if not dir.exists() or not dir.is_dir():
            raise Exception(f'Font family directory is not found: {dir}')

        filepaths = lib_path.get_files_paths(dir)

        families_loaded = []

        for filepath in filepaths:            
            id = QFontDatabase.addApplicationFont(str(filepath))            
            families_loaded += QFontDatabase.applicationFontFamilies(id)

        # families_loaded = list(set(families_loaded))
        
        # if len(families_loaded) > 1:
        #     raise Exception(f'More than one font family loaded from {dir}:\n{families_loaded}\nRemove unnecessary files.')

        # if name != families_loaded[0]:
        #     raise Exception(f'Loaded font family is different from requested: {name} != {families_loaded[0]}')

    @staticmethod
    def _get(name : str, size : int, weight=None, italic=False, bold=False):
        key = (name, size, weight, italic)
        result = QXFontDB._cached.get(key, None)
        if result is None:
            QXFontDB._load_family(name)

            result = QFont(name, size)
            if weight is not None:
                result.setWeight(weight)
            result.setItalic(italic)
            result.setBold(bold)

            QXFontDB._cached[key] = result
        return result

    @staticmethod
    def get_default_font(size=8, italic=False, bold=False):
        lang = Localization.lang

        if lang == 'zh-CN':
            return QXFontDB.Noto_Sans_SC(size, italic=italic, bold=bold)
        else:
            return QXFontDB.Noto_Sans(size, italic=italic, bold=bold)

    @staticmethod
    def get_fixedwidth_font(size=8):
        return QXFontDB.Noto_Mono(size)

    @staticmethod
    def Digital7_Mono(size, italic=False, bold=False):
        return QXFontDB._get('Digital-7 Mono', size, italic=italic, bold=bold)

    @staticmethod
    def Noto_Mono(size, italic=False, bold=False):
        return QXFontDB._get('Noto Mono', size, italic=italic, bold=bold)

    @staticmethod
    def Noto_Sans(size, italic=False, bold=False):
        return QXFontDB._get('Noto Sans', size, italic=italic, bold=bold)

    @staticmethod
    def Noto_Sans_SC(size, italic=False, bold=False):
        return QXFontDB._get('Noto Sans SC', size, italic=italic, bold=bold)

    @staticmethod
    def Tahoma(size, italic=False, bold=False):
        return QXFontDB._get('Tahoma', size, italic=italic, bold=bold)
