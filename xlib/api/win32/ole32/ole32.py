from ctypes import (POINTER, WINFUNCTYPE, byref, c_byte, c_int64, c_longlong,
                    c_size_t, c_ubyte, c_uint, c_uint32, c_ulong, c_void_p,
                    c_wchar)
from typing import Union

from ..wintypes import (DWORD, ERROR, GUID, HRESULT, REFCLSID, REFGUID, REFIID,
                        IUnknown, dll_import, interface)
from .structs import *


@dll_import('ole32')
def CoInitializeEx(pvReserved : c_void_p, dwCoInit : COINIT ) -> HRESULT: ...

@dll_import('ole32')
def CoUninitialize() -> None: ...

@dll_import('ole32')
def CoCreateInstance (rclsid : REFCLSID, pUnkOuter : POINTER(IUnknown), dwClsContext : CLSCTX, refiid : REFIID, ppv : POINTER(IUnknown) ) -> HRESULT: ...
