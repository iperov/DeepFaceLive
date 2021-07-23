from collections import Iterable

from PyQt6.QtCore import *


class BlockSignals:
    def __init__(self, qt_widget_or_list, block_signals=True):
        if not isinstance(qt_widget_or_list, (tuple,list)):
            qt_widget_or_list = [qt_widget_or_list]
        self.qt_widget_or_list = qt_widget_or_list
        self.block_signals = block_signals

    def __enter__(self):
        if self.block_signals:
            for qt_widget in self.qt_widget_or_list:
                qt_widget.blockSignals(True)

        return self

    def __exit__(self, *_):
        if self.block_signals:
            for qt_widget in self.qt_widget_or_list:
                qt_widget.blockSignals(False)

def enable(widget_or_list):
    if not isinstance(widget_or_list, (tuple,list)):
        widget_or_list = [widget_or_list]
    for widget in widget_or_list:
        if isinstance(widget, (tuple,list)):
            enable(widget)
        else:
            widget.setEnabled(True)

def disable(widget_or_list):
    if not isinstance(widget_or_list, (tuple,list)):
        widget_or_list = [widget_or_list]
    for widget in widget_or_list:
        if isinstance(widget, (tuple,list)):
            disable(widget)
        else:
            widget.setEnabled(False)

def hide(widget_or_list):
    if not isinstance(widget_or_list, (tuple,list)):
        widget_or_list = [widget_or_list]
    for widget in widget_or_list:
        if isinstance(widget, (tuple,list)):
            hide(widget)
        else:
            widget.hide()

def show(widget_or_list):
    if not isinstance(widget_or_list, (tuple,list)):
        widget_or_list = [widget_or_list]
    for widget in widget_or_list:
        if isinstance(widget, (tuple,list)):
            show(widget)
        else:
            widget.show()

def show_and_enable(widget_or_list):
    if not isinstance(widget_or_list, (tuple,list)):
        widget_or_list = [widget_or_list]
    for widget in widget_or_list:
        if isinstance(widget, (tuple,list)):
            show_and_enable(widget)
        else:
            widget.show()
            widget.setEnabled(True)

def hide_and_disable(widget_or_list):
    if not isinstance(widget_or_list, (tuple,list)):
        widget_or_list = [widget_or_list]
    for widget in widget_or_list:
        if isinstance(widget, (tuple,list)):
            hide_and_disable(widget)
        else:
            widget.hide()
            widget.setEnabled(False)

def set_contents_margins(obj, contents_margins):

    if contents_margins is not None:
        if isinstance(contents_margins, int):
            contents_margins = (contents_margins,)*4

        if isinstance(contents_margins, Iterable):
            obj.setContentsMargins(*contents_margins)
