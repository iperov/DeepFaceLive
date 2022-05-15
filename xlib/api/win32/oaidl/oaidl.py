from ctypes import POINTER, c_void_p, c_wchar_p
from ..wintypes import (GUID, DWORD, IUnknown, interface, VARIANT, HRESULT, LPCOLESTR)


@interface
class IErrorLog(IUnknown):
    def AddError(self, pszPropName : LPCOLESTR, pExcepInfo : c_void_p) -> HRESULT: ... #EXCEPINFO
    IID = GUID('3127ca40-446e-11ce-8135-00aa004bb851')

@interface
class IPropertyBag(IUnknown):
    def Read(self, pszPropName : LPCOLESTR, pVar : POINTER(VARIANT), pErrorLog : IErrorLog) -> HRESULT: ...
    def Write(self, pszPropName : LPCOLESTR, pVar : POINTER(VARIANT)) -> HRESULT: ...
    IID = GUID('55272a00-42cb-11ce-8135-00aa004bb851')
