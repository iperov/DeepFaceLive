from collections import Iterable

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as lib_qt
from xlib.mp import csw as lib_csw


class QCSWControl(lib_qt.QXWidget):
    """
    base qt widget class for CSWControl
    """

    def __init__(self, csw_control : lib_csw.Control, reflect_state_widgets=None):
        super().__init__()
        self._csw_control = csw_control

        self._csw_state_widgets = []

        csw_control.call_on_change_state(self._on_csw_state_change)

        if reflect_state_widgets is not None:
            self.reflect_state_to_widget(reflect_state_widgets)

    def _on_csw_state_change(self, state):
        """overridable"""
        self._state_to_widget( self._csw_state_widgets+[self] )

    def reflect_state_to_widget(self, widget_or_list):
        """reflect CSW Control state to widgets"""
        if isinstance(widget_or_list, Iterable):
            widget_or_list = list(widget_or_list)
        else:
            widget_or_list = [widget_or_list]

        self._csw_state_widgets += widget_or_list
        self._state_to_widget(widget_or_list)

    def _state_to_widget(self, widgets):
        state = self._csw_control.get_state()
        if state == lib_csw.Control.State.ENABLED:
            for widget in widgets:
                widget.show()
                widget.setEnabled(True)
        elif state == lib_csw.Control.State.FREEZED:
            for widget in widgets:
                widget.setEnabled(False)
                widget.show()
        elif state == lib_csw.Control.State.DISABLED:
            for widget in widgets:
                widget.setEnabled(False)
                widget.hide()


