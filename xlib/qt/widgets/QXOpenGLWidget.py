from PyQt6.QtGui import *
from PyQt6.QtOpenGL import *
from PyQt6.QtOpenGLWidgets import *
from PyQt6.QtWidgets import *

from ._part_QXWidget import _part_QXWidget

_size_policy_from_str = {
    'fixed' : QSizePolicy.Policy.Fixed,
    'minimum' : QSizePolicy.Policy.Minimum,
    'maximum' : QSizePolicy.Policy.Maximum,
    'preferred' : QSizePolicy.Policy.Preferred,
    'minimumexpanding' : QSizePolicy.Policy.MinimumExpanding,
    'expanding' : QSizePolicy.Policy.Expanding,
    'ignored' : QSizePolicy.Policy.Ignored,
}

class QXOpenGLWidget(QOpenGLWidget, _part_QXWidget):
    def __init__(self, 
                       font=None, tooltip_text=None,
                       size_policy=None,
                       minimum_size=None, minimum_width=None, minimum_height=None,
                       maximum_size=None, maximum_width=None, maximum_height=None,
                       fixed_size=None, fixed_width=None, fixed_height=None,
                       hided=False, enabled=True
                       ):

        super().__init__()
        self._default_pal = QPalette( self.palette() )
        
        if size_policy is not None:
            x1, x2 = size_policy
            if isinstance(x1, str):
                x1 = _size_policy_from_str[x1.lower()]
            if isinstance(x2, str):
                x2 = _size_policy_from_str[x2.lower()]
            size_policy = (x1, x2)
                
        _part_QXWidget.__init__(self,   font=font, tooltip_text=tooltip_text,
                                        size_policy=size_policy,
                                        minimum_size=minimum_size, minimum_width=minimum_width, minimum_height=minimum_height,
                                        maximum_size=maximum_size, maximum_width=maximum_width, maximum_height=maximum_height,
                                        fixed_size=fixed_size, fixed_width=fixed_width, fixed_height=fixed_height,
                                        hided=hided, enabled=enabled )
    def focusInEvent(self, ev : QFocusEvent):
        super().focusInEvent(ev)
        _part_QXWidget.focusInEvent(self, ev)

    def resizeEvent(self, ev : QResizeEvent):
        super().resizeEvent(ev)
        _part_QXWidget.resizeEvent(self, ev)
