from typing import List


class TorchDeviceInfo:
    """
    Represents picklable torch device info
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
        if self is not None and other is not None and isinstance(self, TorchDeviceInfo) and isinstance(other, TorchDeviceInfo):
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

# class TorchDevicesInfo:
#     """
#     picklable list of TorchDeviceInfo
#     """
#     def __init__(self, devices : List[TorchDeviceInfo] = None):
#         if devices is None:
#             devices = []
#         self._devices = devices

#     def __getstate__(self):
#         return self.__dict__.copy()

#     def __setstate__(self, d):
#         self.__init__()
#         self.__dict__.update(d)

#     def add(self, device_or_devices : TorchDeviceInfo):
#         if isinstance(device_or_devices, TorchDeviceInfo):
#             if device_or_devices not in self._devices:
#                 self._devices.append(device_or_devices)
#         elif isinstance(device_or_devices, TorchDevicesInfo):
#             for device in device_or_devices:
#                 self.add(device)

#     def copy(self):
#         return copy.deepcopy(self)

#     def get_count(self): return len(self._devices)

#     def get_largest_total_memory_device(self) -> TorchDeviceInfo:
#         raise NotImplementedError()
#         result = None
#         idx_mem = 0
#         for device in self._devices:
#             mem = device.get_total_memory()
#             if result is None or (mem is not None and mem > idx_mem):
#                 result = device
#                 idx_mem = mem
#         return result

#     def get_smallest_total_memory_device(self) -> TorchDeviceInfo:
#         raise NotImplementedError()
#         result = None
#         idx_mem = sys.maxsize
#         for device in self._devices:
#             mem = device.get_total_memory()
#             if result is None or (mem is not None and mem < idx_mem):
#                 result = device
#                 idx_mem = mem
#         return result

#     def __len__(self):
#         return len(self._devices)

#     def __getitem__(self, key):
#         result = self._devices[key]
#         if isinstance(key, slice):
#             return self.__class__(result)
#         return result

#     def __iter__(self):
#         for device in self._devices:
#             yield device

#     def __str__(self):  return f'{self.__class__.__name__}:[' + ', '.join([ device.__str__() for device in self._devices ]) + ']'
#     def __repr__(self): return f'{self.__class__.__name__}:[' + ', '.join([ device.__repr__() for device in self._devices ]) + ']'


_torch_devices = None

def get_cpu_device() -> TorchDeviceInfo:
    return TorchDeviceInfo(index=-1, name='CPU', total_memory=0)

def get_available_devices(include_cpu=True, cpu_only=False) -> List[TorchDeviceInfo]:
    """
    returns a list of available TorchDeviceInfo
    """
    global _torch_devices
    if _torch_devices is None:
        import torch
        devices = []

        if not cpu_only:
            for i in range (torch.cuda.device_count()):
                device_props = torch.cuda.get_device_properties(i)
                devices.append ( TorchDeviceInfo(index=i, name=device_props.name, total_memory=device_props.total_memory))

        if include_cpu or cpu_only:
            devices.append ( get_cpu_device() )

        _torch_devices = devices
    return _torch_devices

