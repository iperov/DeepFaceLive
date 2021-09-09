import ctypes as ct
from ctypes import (POINTER, WINFUNCTYPE, byref, c_byte, c_int64,
                    c_longlong, c_size_t, c_ubyte, c_uint, c_uint32, c_ulong,
                    c_void_p, c_wchar)

class DXGI_ADAPTER_FLAG(c_uint):
    DXGI_ADAPTER_FLAG_NONE	      = 0
    DXGI_ADAPTER_FLAG_REMOTE	  = 1
    DXGI_ADAPTER_FLAG_SOFTWARE	  = 2
    DXGI_ADAPTER_FLAG_FORCE_DWORD = 0xffffffff

class DXGI_ADAPTER_DESC(ct.Structure):
    _fields_ = [('Description', c_wchar * 128),
                ('VendorId', c_uint),
                ('DeviceId', c_uint),
                ('SubSysId', c_uint),
                ('Revision', c_uint),
                ('DedicatedVideoMemory', c_size_t),
                ('DedicatedSystemMemory', c_size_t),
                ('SharedSystemMemory', c_size_t),
                ('AdapterLuid', c_longlong),
               ]
    def __init__(self):
        self.Description : c_wchar * 128 = ''
        self.VendorId : c_uint = c_uint()
        self.DeviceId : c_uint = c_uint()
        self.SubSysId : c_uint = c_uint()
        self.Revision : c_uint = c_uint()
        self.DedicatedVideoMemory : c_size_t = c_size_t()
        self.DedicatedSystemMemory : c_size_t = c_size_t()
        self.SharedSystemMemory : c_size_t = c_size_t()
        self.AdapterLuid : c_longlong = c_longlong()
        super().__init__()

class DXGI_ADAPTER_DESC1(ct.Structure):
    _fields_ = [('Description', c_wchar * 128),
                ('VendorId', c_uint),
                ('DeviceId', c_uint),
                ('SubSysId', c_uint),
                ('Revision', c_uint),
                ('DedicatedVideoMemory', c_size_t),
                ('DedicatedSystemMemory', c_size_t),
                ('SharedSystemMemory', c_size_t),
                ('AdapterLuid', c_longlong),
                ('Flags', c_uint),
               ]

    def __init__(self):
        self.Description : c_wchar * 128 = ''
        self.VendorId : c_uint = c_uint()
        self.DeviceId : c_uint = c_uint()
        self.SubSysId : c_uint = c_uint()
        self.Revision : c_uint = c_uint()
        self.DedicatedVideoMemory : c_size_t = c_size_t()
        self.DedicatedSystemMemory : c_size_t = c_size_t()
        self.SharedSystemMemory : c_size_t = c_size_t()
        self.AdapterLuid : c_longlong = c_longlong()
        self.Flags : c_uint = c_uint()

        super().__init__()
