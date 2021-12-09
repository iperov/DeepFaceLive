from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ..core.QXTimer import QXTimer
from ...db import KeyValueDB

from .forward_declarations import forward_declarations


class QXMainApplication(QApplication):
    inst : 'QXMainApplication' = None

    @staticmethod
    def get_singleton() -> 'QXMainApplication':
        if QXMainApplication.inst is None:
            raise Exception('QXMainApplication must be instantiated')
        return QXMainApplication.inst

    def __init__(self, app_name=None, settings_dirpath : Path = None):
        """
        base class for MainApplication

        QXMainApplication.inst - singleton instance

        settings_dirpath(None)     where the data will be saved
        """
        super().__init__([])

        if QXMainApplication.inst is not None:
            raise Exception('Only one singleton QXMainApplication is allowed')
        QXMainApplication.inst = self

        self._settings_dirpath = settings_dirpath

        if settings_dirpath is not None:
            self._app_data_path = settings_dirpath / 'app.dat'
        else:
            self._app_data_path = None

        self._hierarchy_name_count = {}
        self._app_db = KeyValueDB(self._app_data_path)

        if app_name is not None:
            self.setApplicationName(app_name)

        self.setStyle('Fusion')

        text_color = QColor(200,200,200)
        self.setStyleSheet(f"""
QRadioButton::disabled {{
    color:       gray;
}}

""")
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, QColor(56, 56, 56))

        pal.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(56, 56, 56))
        pal.setColor(QPalette.ColorRole.ToolTipBase, text_color )
        pal.setColor(QPalette.ColorRole.ToolTipText, text_color )
        pal.setColor(QPalette.ColorRole.Text, text_color )
        pal.setColor(QPalette.ColorRole.Button, QColor(56, 56, 56))
        pal.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        pal.setColor(QPalette.ColorRole.PlaceholderText, Qt.GlobalColor.darkGray)
        pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, text_color)
        pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, text_color)
        pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, Qt.GlobalColor.gray)

        pal.setColor(QPalette.ColorRole.WindowText, text_color )
        pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, text_color)
        pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, text_color)
        pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, Qt.GlobalColor.gray)
        pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, Qt.GlobalColor.gray)


        pal.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        pal.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        pal.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(pal)

        self._reinitialize = False
        self._timer = QXTimer(interval=10, timeout=self._on_10ms_timer, start=True)

    def _on_10ms_timer(self):
        self._app_db.process_messages()

        if self._reinitialize:
            self._reinitialize = False
            self.on_reinitialize()

    def register_QXWidget(self, widget) -> str:
        """
        registers QXWidget, checks validity, returns an unique name
        """
        hierarchy = []

        iter_widget = widget
        while True:
            hierarchy.insert(0, iter_widget.__class__.__name__)
            iter_parent_widget = iter_widget.parentWidget()
            if iter_parent_widget is None:
                break
            iter_widget = iter_parent_widget

        if not isinstance(iter_widget, forward_declarations.QXWindow):
            raise Exception('Top widget must be a class of QXWindow')

        if len(hierarchy) == 1:
            # top level widgets(Windows) has no numerification
            return hierarchy[0]
        else:
            hierarchy_name = '.'.join(hierarchy)

            num = self._hierarchy_name_count.get(hierarchy_name, -1)
            num = self._hierarchy_name_count[hierarchy_name] = num + 1

            return f'{hierarchy_name}:{num}'

    def clear_app_data(self):
        """
        clear app data and reinitialize()
        """
        self._app_db.clear()
        self.reinitialize()


    def get_app_data(self, key, default_value=None):
        """
        returns picklable data by picklable key stored in app db

        returns default_value if no data
        """
        return self._app_db.get_value(key, default_value=default_value)

    def set_app_data(self, key, value):
        """
        set picklable data by picklable key stored to app db
        """
        self._app_db.set_value(key, value )

    def run(self):
        """
        run the app
        """
        self.exec()

        self._app_db.finish_pending_jobs()

    def reinitialize(self):
        """
        start reinitialization of app.
        """
        self._reinitialize = True

    def on_reinitialize(self):
        raise NotImplementedError()

    def get_language(self) -> str:
        return self.get_app_data('__app_language', 'en-US')

    def set_language(self, lang : str) -> str:
        """
         lang   xx-YY
                example: en-US ru-RU
        """
        return self.set_app_data('__app_language', lang)