import multiprocessing

class MPSharedMemory:
    def __init__(self, size):
        self._size = size
        self._ar = multiprocessing.RawArray('B', self._size)
        self._mv = memoryview(self._ar).cast('B')

    def get_ar(self) -> multiprocessing.RawArray:
        """
        returns multiprocessing.RawArray
        """
        return self._ar

    def get_mv(self) -> memoryview:
        """
        returns byte-memoryview
        """
        return self._mv

    def __getstate__(self):
        d = self.__dict__.copy()
        d.pop('_mv')
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._mv = memoryview(self._ar).cast('B')