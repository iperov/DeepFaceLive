from typing import Tuple

from PyQt6.QtCore import *

_linear_easing_curve = QEasingCurve(QEasingCurve.Type.Linear)
class QXTimeLine(QTimeLine):
    """
    QXTimeLine with default linear curve


      frame_range(None)  (int,int)   start,end
    """
    def __init__(self, duration,
                       frame_range : Tuple[int,int] = None,
                       loop_count=1,
                       update_interval : int = None,
                       easing_curve=None,
                       frameChanged=None,
                       stateChanged=None,
                       start=False):

        super().__init__(duration)

        if frame_range is not None:
            self.setFrameRange(*frame_range)

        self.setLoopCount(loop_count)

        if update_interval is not None:
            self.setUpdateInterval(update_interval)

        if easing_curve is None:
            easing_curve = _linear_easing_curve
        self.setEasingCurve(easing_curve)

        if frameChanged is not None:
            self.frameChanged.connect(frameChanged)

        if stateChanged is not None:
            self.stateChanged.connect(stateChanged)

        if start:
            self.start()
