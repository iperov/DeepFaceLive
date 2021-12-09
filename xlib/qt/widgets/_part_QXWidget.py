from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ..core.widget import BlockSignals
from .QXMainApplication import QXMainApplication

_size_policy_from_str = {
    'fixed' : QSizePolicy.Policy.Fixed,
    'minimum' : QSizePolicy.Policy.Minimum,
    'maximum' : QSizePolicy.Policy.Maximum,
    'preferred' : QSizePolicy.Policy.Preferred,
    'minimumexpanding' : QSizePolicy.Policy.MinimumExpanding,
    'expanding' : QSizePolicy.Policy.Expanding,
    'ignored' : QSizePolicy.Policy.Ignored,
}

class _part_QXWidget:
    def __init__(self, layout=None,
                       font=None,
                       tooltip_text=None,
                       size_policy=None,
                       minimum_width=None, maximum_width=None, fixed_width=None,
                       minimum_height=None, maximum_height=None, fixed_height=None,
                       minimum_size=None, maximum_size=None, fixed_size=None,
                       hided=False, enabled=True):

        self._registered = False
        self._name_id = None
        self._top_QXWindow = None

        if font is not None:
            self.setFont(font)
        if tooltip_text is not None:
            self.setToolTip(tooltip_text)
            
        if size_policy is not None:
            x1, x2 = size_policy
            if isinstance(x1, str):
                x1 = _size_policy_from_str[x1.lower()]
            if isinstance(x2, str):
                x2 = _size_policy_from_str[x2.lower()]
            size_policy = (x1, x2)
            self.setSizePolicy(*size_policy)
            
        if layout is not None:
            self.setLayout(layout)

        if minimum_size is not None:
            minimum_width, minimum_height = minimum_size
        if minimum_width is not None:
            self.setMinimumWidth(minimum_width)
        if minimum_height is not None:
            self.setMinimumHeight(minimum_height)

        if maximum_size is not None:
            maximum_width, maximum_height = maximum_size
        if maximum_width is not None:
            self.setMaximumWidth(maximum_width)
        if maximum_height is not None:
            self.setMaximumHeight(maximum_height)
    
        if fixed_size is not None:
            fixed_width, fixed_height = fixed_size
        if fixed_width is not None:
            self.setFixedWidth(fixed_width)
        if fixed_height is not None:
            self.setFixedHeight(fixed_height)

        if hided:
            self.hide()
        self.setEnabled(enabled)

    def get_top_QXWindow(self) -> 'QXWindow':
        if self._top_QXWindow is not None:
            return self._top_QXWindow

        obj = self
        while True:
            obj = obj.parentWidget()
            if getattr(obj, '_QXW', False):
                self._top_QXWindow = obj
                return obj
            if obj is None:
                raise Exception('top_QXWindow is not found.')


    def get_name_id(self) -> str:
        """
        returns name_id of widget
        """
        return self._name


    def get_widget_data(self, key, default_value=None):
        """
        Get picklable data by picklable key from widget's storage

        if widget is not registered, default_value will be returned
        """
        if not self._registered:
            return default_value

        return QXMainApplication.inst.get_app_data ( (self._name_id, key), default_value=default_value )

    def set_widget_data(self, key, data):
        """
        Set picklable data by picklable key to widget's storage

        if widget is not registered, nothing will be happened
        """
        QXMainApplication.inst.set_app_data ( (self._name_id, key), data )

    def focusInEvent(self, ev : QFocusEvent):
        if ev.reason() == Qt.FocusReason.TabFocusReason:
            with BlockSignals(self):
                self.clearFocus()

    def resizeEvent(self, ev : QResizeEvent):
        if not self._registered:
            self._registered = True
            self._name_id = QXMainApplication.inst.register_QXWidget(self)
            self._on_registered()

    def _on_registered(self):
        """
        called when widget is registered on QXMainApplication.
        At this point you can use widget's storage.
        """

    @staticmethod
    def connect_signal(funcs, qt_signal):
        if funcs is not None:
            if not isinstance(funcs, (tuple,list)):
                funcs = [funcs]
            for func in funcs:
                qt_signal.connect(func)
