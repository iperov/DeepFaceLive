#from ctypes import c_void_p, c_wchar_p, POINTER
from ..wintypes import BOOL, DWORD,  MMRESULT, dll_import


@dll_import('Winmm')
def timeBeginPeriod(uPeriod : DWORD) -> MMRESULT: ...