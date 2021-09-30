class DeviceInfo:
    """
    Represents picklable OpenCL device info
    """

    def __init__(self, index : int = None, name : str = None, total_memory : int = None, performance_level : int = None):
        self._index = index
        self._name = name
        self._total_memory = total_memory
        self._performance_level = performance_level
        
    def __getstate__(self): 
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)
        
    def get_index(self) -> int:
        return self._index

    def get_name(self) -> str:
        return self._name

    def get_total_memory(self) -> int:
        return self._total_memory
        
    def get_performance_level(self) -> int:
        return self._performance_level
        
    def __eq__(self, other):
        if self is not None and other is not None and isinstance(self, DeviceInfo) and isinstance(other, DeviceInfo):
            return self._index == other._index
        return False

    def __hash__(self):
        return self._index

    def __str__(self):
        return f"[{self._index}] {self._name} [{(self._total_memory / 1024**3) :.3}Gb]"

    def __repr__(self):
        return f'{self.__class__.__name__} object: ' + self.__str__()

