from ..wintypes import DWORD,  MMRESULT, dll_import

@dll_import('Winmm')
def timeBeginPeriod(uPeriod : DWORD) -> MMRESULT: ...