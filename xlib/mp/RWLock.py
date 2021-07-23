import multiprocessing

class RWLock():
    """
    Multiprocessing non-recursive reader-writer lock
    """
    def __init__(self):
        self._a = multiprocessing.RawArray('I', 2)
        #_a[0] : readers counter
        #_a[1] : writer flag
        self._v = memoryview(self._a).cast('B').cast('I')
        self._l = multiprocessing.Lock()

    def read_lock(self):
        v = self._v
        l = self._l
        while True:
            # Non blocky wait writer flag release
            while v[1] != 0:
                pass

            l.acquire()
            if v[1] != 0:
                # Writer flag is still acquired, go to non-blocky waiting
                l.release()
                continue

            # Inc readers counter
            v[0] += 1
            l.release()
            return

    def read_unlock(self):
        v = self._v
        l = self._l
        l.acquire()
        c = v[0]
        if c == 0:
            raise Exception('Invalid lock state')
        # Dec readers counter
        v[0] = c-1
        l.release()

    def write_lock(self):
        v = self._v
        l = self._l

        while True:
            # Non blocky wait writer flag release
            while v[1] != 0:
                pass
            l.acquire()
            if v[1] != 0:
                # Writer flag is still acquired, go to non-blocky waiting
                l.release()
                continue
            # set writer flag
            v[1] = 1
            l.release()

            # Wait all readers gone
            while v[0] != 0:
                pass
            return

    def write_unlock(self):
        v = self._v
        c = v[1]
        if c == 0:
            raise Exception('Invalid lock state')
        # Remove writer flag
        v[1] = 0

    def __getstate__(self):
        d = self.__dict__.copy()
        # pop unpicklable memoryview object
        d.pop('_v')
        return d

    def __setstate__(self, d):
        # restore memoryview of RawArray
        d['_v'] = memoryview(d['_a']).cast('B').cast('I')
        self.__dict__.update(d)