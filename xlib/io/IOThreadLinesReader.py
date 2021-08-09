import threading
import time
from io import IOBase
from typing import List
from collections import deque

class IOThreadLinesReader:
    """
    continuously reads lines from IO in background thread.
    """

    def __init__(self, io : IOBase, max_lines=None):
        self._io = io
        self._lock = threading.Lock()
        self._lines = deque(maxlen=max_lines)

        threading.Thread(target=self._proc, daemon=True).start()

    def _proc(self):
        io = self._io
        lock = self._lock
        lines = self._lines

        while not io.closed and io.readable():
            line = io.readline()
            lock.acquire()
            lines.append(line.decode('utf-8').rstrip())
            lock.release()
            if len(line) == 0:
                break
            time.sleep(0.01)

    def get_lines(self, wait_new=True, till_eof=False) -> List[str]:
        """
        """
        lock = self._lock
        lines = self._lines

        result = []
        while True:

            if len(lines) != 0:
                lock.acquire()
                result += lines
                lines.clear()
                lock.release()

                if till_eof and len(result[-1]) != 0:
                    continue

                return result

            if not till_eof and not wait_new:
                return None
            time.sleep(0.001)

