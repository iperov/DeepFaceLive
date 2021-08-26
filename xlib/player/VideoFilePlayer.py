from pathlib import Path
from typing import Tuple

import numpy as np
from .. import ffmpeg as lib_ffmpeg
from .. import io as lib_io 

from .FramePlayer import FramePlayer

class VideoFilePlayer(FramePlayer):
    """
    Play video track from the video file using subprocess ffmpeg.

    arguments

        filepath        str/Path    path to video file

        is_realtime(True)    bool   False - process every frame as fast as possible
                                            fps parameter will be ignored
                                    True  - process in real time with desired fps

        is_autorewind(True)  bool

        fps(None)   float   specify fps.
                            None - video fps will be used

        target_width(None)  int     if None : resolution will be not modified

    raises

        Exception   path does not exists
                    ffprobe failed
                    file has no video tracks
    """
    SUPPORTED_VIDEO_FILE_SUFFIXES = ['.avi','.mkv','.mp4']

    def __init__(self, filepath):
        self._ffmpeg_proc = None


        self._filepath = filepath = Path(filepath)
        if not filepath.exists():
            raise Exception(f'{filepath} does not exist.')

        if not filepath.is_file():
            raise Exception(f'{filepath} is not a file.')

        if not filepath.suffix in VideoFilePlayer.SUPPORTED_VIDEO_FILE_SUFFIXES:
            raise Exception(f'Supported video files: {VideoFilePlayer.SUPPORTED_VIDEO_FILE_SUFFIXES}')

        probe_info = lib_ffmpeg.probe (str(filepath))
        # Analize probe_info
        stream_v_idx = None
        stream_fps = None
        stream_width = None
        stream_height = None
        for stream in probe_info['streams']:
            if stream_v_idx is None and stream['codec_type'] == 'video':
                stream_v_idx = 0
                stream_width = stream.get('width', None)
                if stream_width is not None:
                    stream_width = int(stream_width)
                stream_height = stream.get('height', None)
                if stream_height is not None:
                    stream_height = int(stream_height)
                stream_start_time = stream.get('start_time', None)
                stream_duration   = stream.get('duration', None)
                stream_fps = stream.get('avg_frame_rate', None)
                if stream_fps is None:
                    stream_fps = stream.get('r_frame_rate', None)
                if stream_fps is not None:
                    stream_fps = eval(stream_fps)
                break

        if any( x is None for x in [stream_v_idx, stream_width, stream_height, stream_start_time, stream_duration, stream_fps] ):
            raise Exception(f'Incorrect video file.')

        stream_frame_count = round( ( float(stream_duration)-float(stream_start_time) ) / (1.0/stream_fps) )

        self._stream_idx = stream_v_idx
        self._stream_width = stream_width
        self._stream_height = stream_height
        self._stream_fps = stream_fps
        self._ffmpeg_need_restart = False
        self._ffmpeg_frame_idx = -1

        super().__init__(default_fps=stream_fps, frame_count=stream_frame_count)

    def _on_dispose(self):
        self._ffmpeg_stop()
        super()._on_dispose()

    def _ffmpeg_stop(self):
        if self._ffmpeg_proc is not None:
            self._ffmpeg_proc.kill()
            self._ffmpeg_proc = None

    def _ffmpeg_restart(self, start_frame_number=0):
        #print('_ffmpeg_restart')
        self._ffmpeg_stop()

        _target_width = self._target_width
        if _target_width == 0:
            _width  = self._ffmpeg_width = self._stream_width
            _height = self._ffmpeg_height = self._stream_height
        else:
            _height = self._ffmpeg_height = int( _target_width / (self._stream_width / self._stream_height) )
            _width  = self._ffmpeg_width = _target_width

        args = []
        if start_frame_number != 0:
            # -ss before -i to fast and accurate seek
            # using time instead of frame, because '-vf select' does not work correctly with some videos
            args += ['-ss', str(start_frame_number*(1.0 / self._stream_fps)) ]

        args += ['-i', str(self._filepath),
                 '-s', f'{_width}:{_height}'
                ]

        # Set exact FPS for constant framerate
        args += ['-r', str(self._stream_fps)]

        args += ['-f', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-map', f'0:v:{self._stream_idx}',
                'pipe:']

        self._ffmpeg_proc = ffmpeg_proc = lib_ffmpeg.run (args, pipe_stdout=True, pipe_stderr=True)
        self._ffmpeg_proc_stderr_lines = None
        if ffmpeg_proc is not None:
            self._ffmpeg_proc_stderr_lines = lib_io.IOThreadLinesReader(ffmpeg_proc.stderr, max_lines=5)
            return True
        return False

    def _ffmpeg_next_frame(self, frames_idx_offset=1):
        frame_buffer = None

        while frames_idx_offset != 0:
            frame_buffer = self._ffmpeg_proc.stdout.read(self._ffmpeg_height*self._ffmpeg_width*3)

            if len(frame_buffer) == 0:
                # unpredicted end reached
                err = '\r\n'.join(self._ffmpeg_proc_stderr_lines.get_lines(till_eof=True)[-5:])
                self._ffmpeg_stop()
                return None, err
            frames_idx_offset -= 1

        if frame_buffer is not None:
            frame_image = np.ndarray( (self._ffmpeg_height, self._ffmpeg_width, 3), dtype=np.uint8, buffer=frame_buffer).copy()
            return frame_image, None
        return None, None

    def _on_target_width_changed(self):
        self._ffmpeg_need_restart = True

    def _on_get_frame(self, idx) -> Tuple[np.ndarray, str]:

        frame_diff = idx - self._ffmpeg_frame_idx
        self._ffmpeg_frame_idx = idx

        if self._ffmpeg_proc is None or \
           frame_diff <= 0 or frame_diff >= 100:
            self._ffmpeg_need_restart = True

        if self._ffmpeg_need_restart:
            self._ffmpeg_need_restart = False
            if not self._ffmpeg_restart(idx):
                return (None, 'ffmpeg error')
            frame_diff = 1
        else:
            frame_diff = max(1, frame_diff)

        #frame_diff += 1
        image, err = self._ffmpeg_next_frame(frame_diff)
        if image is None:
            return (None, f'ffmpeg error: {err}')

        return (image, f'{self._filepath.name}_{idx:06}')



