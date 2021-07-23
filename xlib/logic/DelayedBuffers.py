from collections import deque
from datetime import datetime


class DelayedBuffers:
    """
    Buffers temporal data and "shows" it evenly with target delay.

    first frame created
    0 ms
    |          1500ms first frame arrived, set minimum target delay
                |
                    more data arrived
                    |  ||    || |  |
                                        2000ms target delay (set by user)
                                        |
                ^-----buffered data-----^
                                        |  |  |  |  |  |  |  |  |
                                        ^----show data evenly---^
    """
    class ProcessResult:
        __slots__ = ['new_data']

        def __init__(self):
            self.new_data = None

    def __init__(self):

        self._buffers = deque()
        self._target_delay = 0

        self._last_ts = datetime.now().timestamp()
        self._last_data = None

        self._avg_delay = 1.0

    def _update_avg_frame_delay(self):
        buffers = self._buffers
        if len(buffers) >= 2:
            x = tuple(buffer[0] for buffer in buffers)
            self._avg_delay = min(1.0, (max(x)-min(x)) / (len(x)-1) )

    def get_avg_delay(self): return self._avg_delay

    def add_buffer(self, timestamp : float, data):
        buffers = self._buffers
        buffers_len = len(buffers)
        
        for i in range(buffers_len):
            if timestamp < buffers[i][0]:
                buffers.insert( i, (timestamp, data))
                self._update_avg_frame_delay()
                return
        
        buffers.append( (timestamp, data) )
        self._update_avg_frame_delay()

    def set_target_delay(self, target_delay_sec : float):
        self._target_delay = target_delay_sec


    def process(self) -> 'DelayedBuffers.ProcessResult':
        """
        processes inner logic

        returns DelayedBuffers.ProcessResult()
        """
        result = DelayedBuffers.ProcessResult()
        buffers = self._buffers
        now = datetime.now().timestamp()

        
        if now - self._last_ts >= self._avg_delay:
            self._last_ts += self._avg_delay

            if len(buffers) != 0:
                # Find nearest to target_delay
                nearest_i = -1
                nearest_diff = 999999
                target_delay = self._target_delay

                buffers_to_remove = []
                for i, buffer in enumerate(buffers):
                    ts = buffer[0]

                    diff = abs(now - ts - target_delay)
                    if diff <= nearest_diff:
                        nearest_i = i
                        nearest_diff = diff
                        buffers_to_remove.append(buffer)
                    else:
                        break
                
                if len(buffers_to_remove) >= 2:
                    buffers_to_remove.pop(-1)
                    for buffer in buffers_to_remove:
                        buffers.remove(buffer)
                    self._update_avg_frame_delay()
                
                if len(buffers) != 0:
                    _, new_data = buffers[0]
                    if not self._last_data is new_data:
                        self._last_data = new_data
                        result.new_data = new_data

        return result
