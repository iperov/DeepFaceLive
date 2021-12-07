from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from ..core.QXTimeLine import QXTimeLine
from ..gui import QXImage, QXImageSequence
from ._part_QXWidget import _part_QXWidget


class QXPushButton(QPushButton, _part_QXWidget):
    def __init__(self, image : QXImage = None, flat=False,
                       text=None, padding=4, checkable=False,
                       toggled=None, released=None,
                       **kwargs):
        super().__init__()
        _part_QXWidget.__init__(self, **kwargs)
        _part_QXWidget.connect_signal(released, self.released)
        _part_QXWidget.connect_signal(toggled, self.toggled)

        self._image = None
        self._image_sequence = None
        self._tl = None

        if text is not None:
            self.setText(text)

        if image is not None:
            self._set_image(image)

        self.setCheckable(checkable)

        if flat:
            self.setStyleSheet(f"""
QPushButton {{
    border: 0px;
    background-color: #434343;
    padding: {padding}px;
}}

QPushButton:hover {{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #434343, stop: 0.3 #515151, stop: 0.6 #515151, stop: 1.0 #434343);

}}
QPushButton:pressed {{
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #434343, stop: 0.3 #353535, stop: 0.6 #353535, stop: 1.0 #434343);
}}
""")

    #def sizeHint(self) -> QSize:
    #    return QSize(0,0)

    def setText(self, text):
        QPushButton.setText(self, text)
        self.setMinimumWidth(self.fontMetrics().horizontalAdvance(text)+8)

        new_min_height = self.fontMetrics().height()+4
        min_height = self.minimumHeight()
        if new_min_height > min_height:
            self.setMinimumHeight(new_min_height)

    def _update_icon_size(self):
        if self._image is not None:
            rect = self.rect()
            image = self._image
            w, h = rect.width(), rect.height()

            if h != 0:
                rect_aspect = w / h

                size = image.size()
                pixmap_aspect = size.width() / size.height()

                if pixmap_aspect != rect_aspect:
                    if pixmap_aspect > rect_aspect:
                        pw, ph = w, int(h * (rect_aspect / pixmap_aspect))
                        px, py = 0, h/2-ph/2
                    elif pixmap_aspect < rect_aspect:
                        pw, ph = int( w * (pixmap_aspect / rect_aspect) ), h
                        px, py = w/2-pw/2, 0
                else:
                    px, py, pw, ph = 0, 0, w, h

                self.setIconSize( QSize(pw-4,ph-4) )

    def _set_image(self, image : QXImage ):
        self._image = image
        self.setIcon( image.as_QIcon() )
        self._update_icon_size()

    def set_image(self, image : QXImage ):
        self.stop_image_sequence()
        self._set_image(image)

    def set_image_sequence(self, image_sequence : QXImageSequence, loop_count : int = 1):
        """
        set and play pixmap sequence
        """
        self._image_sequence = image_sequence

        self._tl = QXTimeLine(  duration=image_sequence.get_duration(),
                                frame_range=(0, image_sequence.get_frame_count()-1),
                                loop_count=0,
                                update_interval=int( (1.0/image_sequence.get_fps()) * 1000),
                                frameChanged=self._tl_frameChanged,
                                start=True )

    def stop_image_sequence(self):
        if self._tl is not None:
            self._tl.stop()
            self._tl = None
            self._image_sequence = None

    def _tl_frameChanged(self, frame_id):
        self._set_image(self._image_sequence.get_frame(frame_id))

    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
        self._update_icon_size()
