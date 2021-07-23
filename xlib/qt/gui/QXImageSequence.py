from typing import List

from .QXImage import QXImage


class QXImageSequence:
    """
    contains a list of QXImage with defined FPS
    """

    def __init__(self, frames : List[QXImage], fps : float):
        super().__init__()
        self._frames = frames
        self._fps = fps
        self._frame_count = len(frames)

    def get_fps(self) -> float: return self._fps
    def get_frame_count(self) -> int: return self._frame_count
    def get_frame(self, i) -> QXImage: return self._frames[i]
    def get_duration(self) -> int:
        """
        return duration in ms
        """
        return int( (self._frame_count / self._fps) * 1000 )
