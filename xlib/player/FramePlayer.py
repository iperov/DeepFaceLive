from datetime import datetime
from typing import Tuple

import numpy as np
from ..image import ImageProcessor
from ..python import Disposable


class FramePlayer(Disposable):
    """
    Base class for players based on fixed number of frames
    """

    class Frame:
        __slots__ = ['image','timestamp','fps','frame_num','frame_count','name','error']

        image       : np.ndarray
        timestamp   : float
        fps         : float
        frame_num   : int
        frame_count : int
        name        : str

        def __init__(self):
            self.image       = None
            self.timestamp   = None
            self.fps         = None
            self.frame_num   = None
            self.frame_count = None
            self.name = None

    def __init__(self, default_fps, frame_count):
        if frame_count == 0:
            raise Exception('Frames count are 0.')

        self._default_fps = default_fps
        self._frame_count = frame_count

        self._is_realtime = True
        self._is_autorewind = False

        self._fps = 0

        self._target_width = 0

        self._is_playing = False
        self._frame_idx = 0
        self._frame_timestamp = None
        self._req_is_playing = None
        self._req_frame_seek_idx = None

        self._cached_frames = {}
        self._cached_frames_idxs = []

    def is_playing(self): return self._is_playing
    def get_frame_count(self): return self._frame_count
    def get_frame_idx(self): return self._frame_idx

    def get_is_autorewind(self): return self._is_autorewind
    def set_is_autorewind(self, is_autorewind):
        if not isinstance(is_autorewind, bool):
            raise ValueError('is_autorewind must be an instance of bool')
        self._is_autorewind = is_autorewind
        return self._is_autorewind

    def get_is_realtime(self): return self._is_realtime
    def set_is_realtime(self, is_realtime):
        if not isinstance(is_realtime, bool):
            raise ValueError('is_realtime must be an instance of bool')
        self._is_realtime = is_realtime
        return self._is_realtime

    def get_fps(self): return self._fps
    def set_fps(self, fps):
        """
        set new FPS.
        Returns adjusted FPS.
        """
        if not isinstance(fps, (int, float) ):
            raise ValueError('fps must be an instance of int/float')
        self._fps = float(np.clip(fps, 0, 240))
        self._on_fps_changed()
        return self._fps

    def get_target_width(self):  return self._target_width
    def set_target_width(self, target_width):
        """
        0 - auto
        4..4096

        returns adjusted target_width
        """
        if not isinstance(target_width, (int,float) ):
            raise ValueError('target_width must be an instance of int/float')

        target_width = int(target_width)
        target_width = (target_width // 4) * 4
        target_width = int(np.clip(target_width, 0, 4096))
        self._target_width = target_width
        self._on_target_width_changed()
        return self._target_width

    def _on_play_start(self):
        """@overridable"""
    def _on_play_stop(self):
        """@overridable"""
    def _on_fps_changed(self):
        """@overridable"""
    def _on_target_width_changed(self):
        """@overridable"""

    def _on_get_frame(self, idx) -> Tuple[np.ndarray, str]:
        """
        @overridable

        return (image_of_frame, name_or_error)

        if image_of_frame is None, then specify an error to 'name_or_error'
        otherwise 'name_or_error' is a name of frame
        """
        return None

    def req_frame_seek(self, idx, mode):
        """
        Request to seek to specified frame idx
        """
        self._req_frame_seek_idx = (idx, mode)


    def req_play_start(self):
        """
        Request to start playing.
        """
        self._req_is_playing = True

    def req_play_stop(self):
        """
        Request to stop playing.
        """
        self._req_is_playing = False

    class ProcessResult:
        __slots__ = ['new_is_playing','new_frame_idx','new_frame','new_error']

        def __init__(self):
            self.new_is_playing = None
            self.new_frame_idx = None
            self.new_frame = None
            self.new_error : str = None

    def process(self) -> 'FramePlayer.ProcessResult':
        """
        processes inner logic

        returns FramePlayer.ProcessResult()
        """
        # Process player logic.
        new_is_playing = None
        new_frame_idx = None
        new_frame_timestamp = None
        update_frame = False

        fps = self._fps
        if fps == 0:
            fps = self._default_fps

        result = FramePlayer.ProcessResult()

        if self._is_playing:
            if self._is_realtime:
                diff_frames = int( (datetime.now().timestamp() - self._frame_timestamp) / (1.0/fps) )
                if diff_frames != 0:
                    new_frame_idx = self._frame_idx + diff_frames
                    new_frame_timestamp = self._frame_timestamp + diff_frames * (1.0/fps)
            else:
                new_frame_idx = self._frame_idx + 1
                new_frame_timestamp = datetime.now().timestamp()

        if self._req_frame_seek_idx is not None:
            # User frame seek overrides new frame idx
            seek_idx, seek_mode = self._req_frame_seek_idx
            if seek_mode == 0:
                new_frame_idx = seek_idx
            elif seek_mode == 1:
                new_frame_idx = self._frame_idx + seek_idx
            elif seek_mode == 2:
                new_frame_idx = self._frame_count - seek_idx -1

            new_frame_timestamp = datetime.now().timestamp()

        if new_frame_idx is not None:
            # new_frame_idx mean the frame should be updated, even if idx is not changed
            update_frame = True

            if new_frame_idx < 0 or new_frame_idx >= self._frame_count:
                # End of frames reached
                if self._is_autorewind:
                    # AutoRewind
                    new_frame_idx %= self._frame_count
                else:
                    # No AutoRewind. Stop at last frame, but don't update frame
                    if new_frame_idx < 0:
                        new_frame_idx = 0
                    else:
                        new_frame_idx = self._frame_count-1
                    update_frame = False
                    new_is_playing = False

            if self._frame_idx != new_frame_idx:
                self._frame_idx = result.new_frame_idx = new_frame_idx

        if new_frame_timestamp is not None:
            self._frame_timestamp = new_frame_timestamp

        if new_is_playing is None:
            # new_is_playing is not changed by system, now can handle user request
            new_is_playing = self._req_is_playing

        if new_is_playing is not None and new_is_playing and not self._is_playing:
            # Start playing
            result.new_is_playing = self._is_playing = True
            self._frame_timestamp = datetime.now().timestamp()
            self._on_play_start()
            update_frame = True

        if update_frame:
            # Frame changed, construct Frame() with current values
            _frame_idx = self._frame_idx
            _cached_frames = self._cached_frames
            _cached_frames_idxs = self._cached_frames_idxs

            frame_tuple = _cached_frames.get(_frame_idx, None)
            if frame_tuple is None:
                frame_tuple = self._on_get_frame(_frame_idx)
                _cached_frames[_frame_idx] = frame_tuple
                _cached_frames_idxs.insert(0, _frame_idx)
                if len(_cached_frames_idxs) > 5:
                    _cached_frames.pop(_cached_frames_idxs.pop(-1))

            frame_image, name_or_err = frame_tuple

            if frame_image is None:
                # frame is not provided, stop playing
                new_is_playing = False
                result.new_error = name_or_err
            else:
                # frame is provided.
                p_frame = result.new_frame = FramePlayer.Frame()
                p_frame.fps = fps
                p_frame.timestamp = self._frame_timestamp

                p_frame.frame_num = _frame_idx
                p_frame.frame_count = self._frame_count

                ip = ImageProcessor(frame_image)
                if self._target_width != 0:
                    ip.fit_in(TW=self._target_width)
                frame_image = ip.ch(3).get_image('HWC')

                p_frame.image = frame_image
                p_frame.name = name_or_err

        if new_is_playing is not None and self._is_playing and not new_is_playing:
            # Stop playing
            result.new_is_playing = self._is_playing = False
            self._on_play_stop()

        if self._req_is_playing is not None or self._req_frame_seek_idx is not None:
            self._req_is_playing = None
            self._req_frame_seek_idx = None

        return result
