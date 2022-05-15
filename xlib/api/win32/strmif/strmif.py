from ctypes import POINTER

from ..objidl import IEnumMoniker
from ..wintypes import DWORD, GUID, HRESULT, REFIID, IUnknown, interface


@interface
class ICreateDevEnum(IUnknown):
    def CreateClassEnumerator(self, refiid : REFIID, enumMoniker : POINTER(IEnumMoniker), flags : DWORD ) -> HRESULT: ...
    IID = GUID('29840822-5B84-11D0-BD3B-00A0C911CE86')
