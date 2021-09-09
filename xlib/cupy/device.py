from typing import List

from .. import appargs as lib_appargs


class CuPyDeviceInfo:
    """
    Represents picklable CuPy device info
    """
    def __init__(self, index=None, name=None, total_memory=None):
        self._index : int = index
        self._name : str = name
        self._total_memory : int = total_memory

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

    def is_cpu(self) -> bool: return self._index == -1

    def get_index(self) -> int:
        return self._index

    def get_name(self) -> str:
        return self._name

    def get_total_memory(self) -> int:
        return self._total_memory

    def __eq__(self, other):
        if self is not None and other is not None and isinstance(self, CuPyDeviceInfo) and isinstance(other, CuPyDeviceInfo):
            return self._index == other._index
        return False

    def __hash__(self):
        return self._index

    def __str__(self):
        if self.is_cpu():
            return "CPU"
        else:
            return f"[{self._index}] {self._name} [{(self._total_memory / 1024**3) :.3}Gb]"

    def __repr__(self):
        return f'{self.__class__.__name__} object: ' + self.__str__()


_cupy_devices = None
def get_available_devices() -> List[CuPyDeviceInfo]:
    """
    returns a list of available CuPyDeviceInfo
    """
    if lib_appargs.get_arg_bool('NO_CUDA'):
        return []
    
    global _cupy_devices
    
    if _cupy_devices is None:
        import cupy as cp # BUG eats 1.8Gb paging file per process, so import on demand
        devices = []

        for i in range (cp.cuda.runtime.getDeviceCount()):
            device_props = cp.cuda.runtime.getDeviceProperties(i)
            devices.append ( CuPyDeviceInfo(index=i, name=device_props['name'].decode('utf-8'), total_memory=device_props['totalGlobalMem']))

        _cupy_devices = devices
    return _cupy_devices

