import platform
import time
from collections import deque
from datetime import datetime

import numpy as np

if platform.system() == 'Windows':
    from xlib.api.win32 import kernel32, wintypes
    _perf_freq = wintypes.LARGE_INTEGER()
    if not kernel32.QueryPerformanceFrequency(_perf_freq):
        raise Exception('QueryPerformanceFrequency')
    _perf_freq = _perf_freq.value

if platform.system() == 'Windows':
    class timeit:
        def __enter__(self):
            self._counter = wintypes.LARGE_INTEGER()
            if not kernel32.QueryPerformanceCounter(self._counter):
                raise Exception('QueryPerformanceCounter')
            
        def __exit__(self, a,b,c):
            new_counter = wintypes.LARGE_INTEGER()
            if not kernel32.QueryPerformanceCounter(new_counter):
                raise Exception('QueryPerformanceCounter')
            t = (new_counter.value-self._counter.value) / _perf_freq
            print(f'timeit!: {t}')
else:
    class timeit:
        def __enter__(self):
            self.t = datetime.now().timestamp()
        def __exit__(self, a,b,c):
            print(f'timeit!: {datetime.now().timestamp()-self.t}')

class measure:
    def __init__(self):
        self.t = time.time()

    def elapsed(self):
        return time.time()-self.t

class AverageMeasurer:
    def __init__(self, samples=120):
        self._samples = samples
        self._ts = None

        self._measurements = [0]*samples
        self._n_sample = 0

    def start(self):
        self._ts = datetime.now().timestamp()

    def discard(self):
        self._ts = None

    def stop(self) -> float:
        """
        stop measure and return current average time sec
        """
        measurements = self._measurements
        if self._ts is None:
            raise Exception('AverageMeasurer was not started')
        t = datetime.now().timestamp() - self._ts
        measurements[self._n_sample] = t
        self._n_sample = (self._n_sample + 1) % self._samples
        self._ts = None
        return max(0.001, np.mean(measurements))

class FPSCounter:
    def __init__(self, samples=120):
        self._steps = deque(maxlen=samples)

    def step(self) -> float:
        """
        make a step for FPSCounter and returns current FPS
        """
        steps = self._steps
        steps.append(datetime.now().timestamp()  )
        if len(steps) >= 2:
            div = steps[-1] - steps[0]
            if div != 0:
                return len(steps) / div
        return 0.0



