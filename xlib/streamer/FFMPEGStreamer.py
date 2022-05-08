import numpy as np

from .. import ffmpeg as lib_ffmpeg


class FFMPEGStreamer:
    def __init__(self):
        self._ffmpeg_proc = None
        self._addr = '127.0.0.1'
        self._port = 1234
        self._width = 320
        self._height = 240

    def set_addr_port(self, addr : str, port : int):
        if self._addr != addr or self._port != port:
            self._addr = addr
            self._port = port
            self.stop()
    
    def stop(self):
        if self._ffmpeg_proc is not None:
            self._ffmpeg_proc.kill()
            self._ffmpeg_proc = None
        
    def _restart(self):
        self.stop()
        args = ['-y', '-re',
                '-f', 'rawvideo',
                '-vcodec','rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', f'{self._width}:{self._height}',
                '-i', '-',
                '-f', 'mpegts',
                '-q:v', '2',
                f'udp://{self._addr}:{self._port}'
        ]
        self._ffmpeg_proc = lib_ffmpeg.run (args, pipe_stdin=True, quiet_stderr=True)#, pipe_stderr=True)

    def push_frame(self, img : np.ndarray):
        H,W,C = img.shape
        if self._width != W or self._height != H:
            self._width = W
            self._height = H
            self.stop()
            
        if self._ffmpeg_proc is None:
            self._restart()
        
        try:
            self._ffmpeg_proc.stdin.write(img)
        except:
            self.stop()
