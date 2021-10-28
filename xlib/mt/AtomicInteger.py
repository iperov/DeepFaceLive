import threading

class AtomicInteger:
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = threading.Lock()
        
    def inc(self, d = 1):
        with self._lock:
            self._value += int(d)
            return self._value

    def dec(self, d = 1):
        return self.inc(-d)    

    def get_value(self) -> int:
        with self._lock:
            return self._value

    def set_value(self, v : int):
        with self._lock:
            self._value = int(v)
            return self._value