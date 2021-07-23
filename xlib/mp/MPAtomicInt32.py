import multiprocessing


class MPAtomicInt32:
    """
    Multiprocess atomic int32 variable
    using multiprocessing.RawArray at specified index
    """
    def __init__(self, ar : multiprocessing.RawArray=None, index=None):
        if ar is None:
            ar = multiprocessing.RawArray('B', 4)
        self._ar = ar
        if index is None:
            index = 0
        self._index = index
        self._mv = memoryview(ar).cast('B')[index:index+4].cast('i')
        self._mv[0] = 0
        self._lock = multiprocessing.Lock()

    def compare_exchange(self, cmp_val, new_val):
        mv = self._mv
        initial_val = mv[0]
        if initial_val == cmp_val:
            self._lock.acquire()
            initial_val = mv[0]
            if initial_val == cmp_val:
                mv[0] = new_val
            self._lock.release()
        return initial_val

    def multi_compare_exchange(self, val_or_list, new_val):
        if not isinstance(val_or_list, (tuple,list)):
            val_or_list = (val_or_list,)

        mv = self._mv
        initial_val = mv[0]
        if any( initial_val == val for val in val_or_list ):
            self._lock.acquire()
            initial_val = mv[0]
            if any( initial_val == val for val in val_or_list ):
                mv[0] = new_val
            self._lock.release()
        return initial_val

    def get(self):
        return self._mv[0]

    def set(self, new_val, with_lock=True):
        if with_lock:
            self._lock.acquire()
        self._mv[0] = new_val
        if with_lock:
            self._lock.release()

    def __getstate__(self):
        d = self.__dict__.copy()
        # pop unpicklable memoryview object
        d.pop('_mv')
        return d

    def __setstate__(self, d):
        # restore memoryview of RawArray
        self.__dict__.update(d)
        self._mv = memoryview(self._ar).cast('B')[self._index:self._index+4].cast('i')
