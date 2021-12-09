from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from ...python import EventListener

from .forward_declarations import forward_declarations
from .QXMainApplication import QXMainApplication
from .QXWidget import QXWidget


class QXWindow(QXWidget):
    def __init__(self, save_load_state=False, **kwargs):
        """
        represents top widget which has no parent
        """
        super().__init__(**kwargs)
        self._save_load_state = save_load_state

        #QXMainApplication.inst.register_QXWindow(self)

        #self.keyPressEvent_listeners = []
        #self.keyReleaseEvent_listeners = []

        self._QXW = True
        self._closeEvent_ev = EventListener()

        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self._qp = QPainter()

        pal = QXMainApplication.inst.palette()
        self._bg_color = pal.color(QPalette.ColorRole.Window)

    def call_on_closeEvent(self, func_or_list):
        self._closeEvent_ev.add(func_or_list)

    # def add_closeEvent_func(self, func):
    #     self.closeEvent_funcs.append (func)

    # def add_keyPressEvent_listener(self, func):
    #     self.keyPressEvent_listeners.append (func)

    # def add_keyReleaseEvent_listener(self, func):
    #     self.keyReleaseEvent_listeners.append (func)

    def center_on_screen(self):
        widget_width, widget_height = self.size().width(), self.size().height()
        screen_size = QXMainApplication.inst.primaryScreen().size()

        self.move( (screen_size.width() - widget_width) // 2,  (screen_size.height() - widget_height) // 2 )

    #def resizeEvent(self, ev : QResizeEvent):
    #    super().resizeEvent(ev)

    def showEvent(self, ev: QShowEvent):
        super().showEvent(ev)
        if self._save_load_state:
            geo = self.get_widget_data('geometry')
            if geo is not None:
                pos, size = geo
                self.move(pos)
                self.resize(size)
            else:
                self.center_on_screen()

    def hideEvent(self, ev: QHideEvent):
        super().hideEvent(ev)
        if self._save_load_state:
            self.set_widget_data('geometry', ( self.pos(), self.size() ) )

    def closeEvent(self, ev : QCloseEvent):
        super().closeEvent(ev)
        if ev.isAccepted():
            self._closeEvent_ev.call()

    def is_minimized(self) -> bool:
        state = self.windowState()
        return (state & Qt.WindowState.WindowMinimized) == Qt.WindowState.WindowMinimized

    def paintEvent(self, ev : QPaintEvent):
        qp = self._qp
        qp.begin(self)
        qp.fillRect(self.rect(), self._bg_color )
        qp.end()

    # def keyPressEvent(self, ev):
    #     super().keyPressEvent(ev)
    #     for func in self.keyPressEvent_listeners:
    #         func(ev)

    # def keyReleaseEvent(self, ev):
    #     super().keyReleaseEvent(ev)
    #     for func in self.keyReleaseEvent_listeners:
    #         func(ev)

forward_declarations.QXWindow = QXWindow
