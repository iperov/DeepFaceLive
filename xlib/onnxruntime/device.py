import ctypes
import os
from typing import List


class ORTDeviceInfo:
    """
    Represents picklable ONNXRuntime device info
    """

    def __init__(self, index=None, name=None, total_memory=None, free_memory=None, compute_capability=None):
        self._index : int = index
        self._name : str = name
        self._total_memory : int = total_memory
        self._free_memory : int = free_memory
        self._compute_capability : int = compute_capability

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

    def is_cpu(self) -> bool: return self._index == -1

    def get_index(self) -> int:
        return self._index

    def get_compute_capability(self) -> int:
        return self._compute_capability

    def get_name(self) -> str:
        return self._name

    def get_total_memory(self) -> int:
        return self._total_memory

    def get_free_memory(self) -> int:
        return self._free_memory

    def __eq__(self, other):
        if self is not None and other is not None and isinstance(self, ORTDeviceInfo) and isinstance(other, ORTDeviceInfo):
            return self._index == other._index
        return False

    def __hash__(self):
        return self._index

    def __str__(self):
        if self.is_cpu():
            return f"CPU"
        else:
            return f"[{self._index}] {self._name} [{(self._total_memory / 1024**3) :.3}Gb]"

    def __repr__(self):
        return f'{self.__class__.__name__} object: ' + self.__str__()


# class ORTDevicesInfo:
#     """
#     a list of ORTDeviceInfo
#     """

#     def __init__(self, devices : List[ORTDeviceInfo] = None):
#         if devices is None:
#             devices = []
#         self._devices = devices

#     def __getstate__(self):
#         return self.__dict__.copy()

#     def __setstate__(self, d):
#         self.__init__()
#         self.__dict__.update(d)

#     def add(self, device_or_devices : ORTDeviceInfo):
#         if isinstance(device_or_devices, ORTDeviceInfo):
#             if device_or_devices not in self._devices:
#                 self._devices.append(device_or_devices)
#         elif isinstance(device_or_devices, ORTDevicesInfo):
#             for device in device_or_devices:
#                 self.add(device)

#     def copy(self):
#         return copy.deepcopy(self)

#     def get_count(self): return len(self._devices)

#     def get_highest_total_memory_device(self) -> ORTDeviceInfo:
#         """
#         returns ORTDeviceInfo with highest available memory, if devices support total_memory parameter
#         """
#         result = None
#         idx_mem = 0
#         for device in self._devices:
#             mem = device.get_total_memory()
#             if result is None or (mem is not None and mem > idx_mem):
#                 result = device
#                 idx_mem = mem
#         return result

#     def get_lowest_total_memory_device(self) -> ORTDeviceInfo:
#         """
#         returns ORTDeviceInfo with lowest available memory, if devices support total_memory parameter
#         """
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



_ort_devices_info = None

def get_cpu_device() -> ORTDeviceInfo:
    return ORTDeviceInfo(index=-1, name='CPU', total_memory=0, free_memory=0, compute_capability=0)

def get_available_devices_info(include_cpu=True, cpu_only=False) -> List[ORTDeviceInfo]:
    """
    returns a list of available ORTDeviceInfo
    """
    global _ort_devices_info
    if _ort_devices_info is None:
        _initialize_ort_devices()
        devices = []
        if not cpu_only:
            for i in range ( int(os.environ['ORT_DEVICES_COUNT']) ):
                devices.append ( ORTDeviceInfo(index=i,
                                                name=os.environ[f'ORT_DEVICE_{i}_NAME'],
                                                total_memory=int(os.environ[f'ORT_DEVICE_{i}_TOTAL_MEM']),
                                                free_memory=int(os.environ[f'ORT_DEVICE_{i}_FREE_MEM']),
                                                compute_capability=int(os.environ[f'ORT_DEVICE_{i}_CC']) ))
        if include_cpu or cpu_only:
            devices.append(get_cpu_device())
        _ort_devices_info = devices

    return _ort_devices_info


def _initialize_ort_devices():
    """
    Determine available ORT devices, and place info about them to os.environ,
    they will be available in spawned subprocesses.

    Using only python ctypes and default lib provided with NVIDIA drivers.
    """
    if int(os.environ.get('ORT_DEVICES_INITIALIZED', 0)) == 0:
        os.environ['ORT_DEVICES_INITIALIZED'] = '1'
        os.environ['ORT_DEVICES_COUNT'] = '0'
        os.environ['CUDA_​CACHE_​MAXSIZE'] = '2147483647'
        try:
            libnames = ('libcuda.so', 'libcuda.dylib', 'nvcuda.dll')
            for libname in libnames:
                try:
                    cuda = ctypes.CDLL(libname)
                except:
                    continue
                else:
                    break
            else:
                return

            nGpus = ctypes.c_int()
            name = b' ' * 200
            cc_major = ctypes.c_int()
            cc_minor = ctypes.c_int()
            freeMem = ctypes.c_size_t()
            totalMem = ctypes.c_size_t()
            device = ctypes.c_int()
            context = ctypes.c_void_p()
            devices = []

            if cuda.cuInit(0) == 0 and \
                cuda.cuDeviceGetCount(ctypes.byref(nGpus)) == 0:
                for i in range(nGpus.value):
                    if cuda.cuDeviceGet(ctypes.byref(device), i) != 0 or \
                        cuda.cuDeviceGetName(ctypes.c_char_p(name), len(name), device) != 0 or \
                        cuda.cuDeviceComputeCapability(ctypes.byref(cc_major), ctypes.byref(cc_minor), device) != 0:
                        continue

                    if cuda.cuCtxCreate_v2(ctypes.byref(context), 0, device) == 0:
                        if cuda.cuMemGetInfo_v2(ctypes.byref(freeMem), ctypes.byref(totalMem)) == 0:
                            cc = cc_major.value * 10 + cc_minor.value
                            devices.append ({'name'     : name.split(b'\0', 1)[0].decode(),
                                            'total_mem' : totalMem.value,
                                            'free_mem'  : freeMem.value,
                                            'cc'        : cc
                                            })
                        cuda.cuCtxDetach(context)
        except Exception as e:
            print(f'CUDA devices initialization error: {e}')
            devices = []

        os.environ['ORT_DEVICES_COUNT'] = str(len(devices))
        for i, device in enumerate(devices):
            os.environ[f'ORT_DEVICE_{i}_NAME'] = device['name']
            os.environ[f'ORT_DEVICE_{i}_TOTAL_MEM'] = str(device['total_mem'])
            os.environ[f'ORT_DEVICE_{i}_FREE_MEM'] = str(device['free_mem'])
            os.environ[f'ORT_DEVICE_{i}_CC'] = str(device['cc'])

_initialize_ort_devices()
