from ctypes import POINTER, c_longlong, c_uint, c_void_p
from typing import Union

from xlib.api.win32.wintypes.wintypes import BOOL

from ..wintypes import (ERROR, GUID, HRESULT, REFGUID, REFIID, IUnknown,
                        dll_import, interface)
from .structs import *


@interface
class IDXGIObject(IUnknown):
    def SetPrivateData          (self, guid : REFGUID, id : c_uint, data : c_void_p) -> HRESULT: ...
    def SetPrivateDataInterface (self, guid : REFGUID, interface : IUnknown) -> HRESULT: ...
    def GetPrivateData          (self, guid : REFGUID, in_out_data_size : POINTER(c_uint), out_data : c_void_p ) -> HRESULT: ...
    def GetParent               (self, iid : REFIID, out_interface : POINTER(IUnknown)) -> HRESULT: ...
    IID = GUID('aec22fb8-76f3-4639-9be0-28eb43a67a2e')

@interface
class IDXGIAdapter(IDXGIObject):
    def EnumOutputs           (self, output : c_uint, output_interface : POINTER(c_void_p) ) -> HRESULT: ... ## IDXGIOutput**
    def GetDesc               (self, out_desc : POINTER(DXGI_ADAPTER_DESC)) -> HRESULT: ...
    def CheckInterfaceSupport (self, guid : REFGUID, out_umdversion : POINTER(c_longlong) ) -> HRESULT: ... #InterfaceName, pUMDVersion
    IID = GUID('2411e7e1-12ac-4ccf-bd14-9798e8534dc0')

@interface
class IDXGIAdapter1(IDXGIAdapter):
    def GetDesc1 (self, out_desc1 : POINTER(DXGI_ADAPTER_DESC1) ) -> HRESULT: ...
    IID = GUID('29038f61-3839-4626-91fd-086879011a05')

    def get_desc1(self) -> Union[DXGI_ADAPTER_DESC1, None]:
        desc1 = DXGI_ADAPTER_DESC1()
        if self.GetDesc1(desc1) == ERROR.SUCCESS:
            return desc1
        return None

    def __str__(self):
        desc = self.get_desc1()
        if desc is not None:
            return f'IDXGIAdapter1 object: {desc.Description}'
        else:
            return f'IDXGIAdapter1 object'

    def __repr__(self): return self.__str__()

@interface
class IDXGIFactory(IDXGIObject):
    def EnumAdapters(self) -> None: ...
    def MakeWindowAssociation(self) -> None: ...
    def GetWindowAssociation(self) -> None: ...
    def CreateSwapChain(self) -> None: ...
    def CreateSoftwareAdapter(self) -> None: ...
    IID = GUID('7b7166ec-21c7-44ae-b21a-c9ae321ae369')

@interface
class IDXGIFactory1(IDXGIFactory):
    def EnumAdapters1(self, adapter_id : c_uint, out_interface : POINTER(IDXGIAdapter1)) -> HRESULT: ...
    def IsCurrent(self) -> BOOL: ...

    IID = GUID('770aae78-f26f-4dba-a829-253c83d1b387')

    def enum_adapters1(self, id : int) -> Union[IDXGIAdapter1, None]:
        result = IDXGIAdapter1()
        if self.EnumAdapters1(id, result) == ERROR.SUCCESS:
            return result
        return None

@interface
class IDXGIFactory2(IDXGIFactory1):
    def IsWindowedStereoEnabled(self) -> None: ...
    def CreateSwapChainForHwnd(self) -> None: ...
    def CreateSwapChainForCoreWindow(self) -> None: ...
    def GetSharedResourceAdapterLuid(self) -> None: ...
    def RegisterStereoStatusWindow(self) -> None: ...
    def RegisterStereoStatusEvent(self) -> None: ...
    def UnregisterStereoStatus(self) -> None: ...
    def RegisterOcclusionStatusWindow(self) -> None: ...
    def RegisterOcclusionStatusEvent(self) -> None: ...
    def UnregisterOcclusionStatus(self) -> None: ...
    def CreateSwapChainForComposition(self) -> None: ...
    IID = GUID('50c83a1c-e072-4c48-87b0-3630fa36a6d0')

@interface
class IDXGIFactory3(IDXGIFactory2):
    def GetCreationFlags(self) -> None: ...
    IID = GUID('25483823-cd46-4c7d-86ca-47aa95b837bd')

@interface
class IDXGIFactory4(IDXGIFactory2):
    def EnumAdapterByLuid(self) -> None: ...
    def EnumWarpAdapter(self) -> None: ...
    IID = GUID('1bc6ea02-ef36-464f-bf0c-21ca39e5168a')

@dll_import('dxgi')
def CreateDXGIFactory1(refiid : REFIID, p_IDXGIFactory1 : POINTER(IDXGIFactory1) ) -> HRESULT: ...
@dll_import('dxgi')
def CreateDXGIFactory2(flags : c_uint, refiid : REFIID, p_IDXGIFactory2 : POINTER(IDXGIFactory2) ) -> HRESULT: ...

def create_DXGIFactory1() -> Union[IDXGIFactory1, None]:
    result = IDXGIFactory1()
    if CreateDXGIFactory1(IDXGIFactory1.IID, result ) == ERROR.SUCCESS:
        return result
    return None

def create_DXGIFactory2() -> Union[IDXGIFactory2, None]:
    result = IDXGIFactory2()
    if CreateDXGIFactory2(0, IDXGIFactory2.IID, result ) == ERROR.SUCCESS:
        return result
    return None

def create_DXGIFactory3() -> Union[IDXGIFactory3, None]:
    result = IDXGIFactory3()
    if CreateDXGIFactory2(0, IDXGIFactory3.IID, result ) == ERROR.SUCCESS:
        return result
    return None

def create_DXGIFactory4() -> Union[IDXGIFactory4, None]:
    result = IDXGIFactory4()
    if CreateDXGIFactory2(0, IDXGIFactory4.IID, result ) == ERROR.SUCCESS:
        return result
    return None
