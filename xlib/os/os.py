import os
import platform
import traceback
from enum import IntEnum

is_win = False
is_linux = False
is_darwin = False

if platform.system() == 'Windows':
    is_win = True
    from xlib.api.win32 import kernel32, winmm, wintypes
elif platform.system() == 'Linux':
    is_linux = True
elif platform.system() == 'Darwin':
    is_darwin = True

_niceness = 0

class ProcessPriority(IntEnum):
    HIGH = 4,
    ABOVE_NORMAL = 3,
    NORMAL = 2,
    BELOW_NORMAL = 1,
    IDLE = 0

def get_process_priority() -> ProcessPriority:
    """
    """
    global _niceness

    if is_win:
        prio = kernel32.GetPriorityClass (kernel32.GetCurrentProcess())
        prio = {kernel32.PriorityClass.HIGH_PRIORITY_CLASS         : ProcessPriority.HIGH        ,
                kernel32.PriorityClass.ABOVE_NORMAL_PRIORITY_CLASS : ProcessPriority.ABOVE_NORMAL,
                kernel32.PriorityClass.NORMAL_PRIORITY_CLASS       : ProcessPriority.NORMAL      ,
                kernel32.PriorityClass.BELOW_NORMAL_PRIORITY_CLASS : ProcessPriority.BELOW_NORMAL,
                kernel32.PriorityClass.IDLE_PRIORITY_CLASS         : ProcessPriority.IDLE        ,
                }[prio]
        return prio
    elif is_linux:
        prio = {-20 : ProcessPriority.HIGH        ,
                -10 : ProcessPriority.ABOVE_NORMAL,
                0   : ProcessPriority.NORMAL      ,
                10  : ProcessPriority.BELOW_NORMAL,
                20  : ProcessPriority.IDLE        ,
                }[_niceness]
    elif is_darwin:
        prio = {-10 : ProcessPriority.HIGH        ,
                -5  : ProcessPriority.ABOVE_NORMAL,
                0   : ProcessPriority.NORMAL      ,
                5   : ProcessPriority.BELOW_NORMAL,
                10  : ProcessPriority.IDLE        ,
                }[_niceness]

        return prio

def set_process_priority(prio : ProcessPriority):
    """
    """
    global _niceness
    try:
        if is_win:
            hProcess = kernel32.GetCurrentProcess()

            val = {ProcessPriority.HIGH         : kernel32.PriorityClass.HIGH_PRIORITY_CLASS,
                   ProcessPriority.ABOVE_NORMAL : kernel32.PriorityClass.ABOVE_NORMAL_PRIORITY_CLASS,
                   ProcessPriority.NORMAL       : kernel32.PriorityClass.NORMAL_PRIORITY_CLASS,
                   ProcessPriority.BELOW_NORMAL : kernel32.PriorityClass.BELOW_NORMAL_PRIORITY_CLASS,
                   ProcessPriority.IDLE         : kernel32.PriorityClass.IDLE_PRIORITY_CLASS,
                   }[prio]

            kernel32.SetPriorityClass (hProcess, val)
        elif is_linux:
            val = {ProcessPriority.HIGH         : -20,
                   ProcessPriority.ABOVE_NORMAL : -10,
                   ProcessPriority.NORMAL       : 0  ,
                   ProcessPriority.BELOW_NORMAL : 10 ,
                   ProcessPriority.IDLE         : 20 ,
                   }[prio]

            _niceness = os.nice(val)
        elif is_darwin:
            val = {ProcessPriority.HIGH         : -10,
                   ProcessPriority.ABOVE_NORMAL : -5 ,
                   ProcessPriority.NORMAL       : 0  ,
                   ProcessPriority.BELOW_NORMAL : 5  ,
                   ProcessPriority.IDLE         : 10 ,
                   }[prio]

            _niceness = os.nice(val)
    except:
        print(f'set_process_priority error: {traceback.format_exc()}')

def set_timer_resolution(milliseconds : int) -> bool:
    """
    sets minimum timer resolution, in milliseconds, for time services, such as sleep or wait.

    return True if success
    """
    if is_win:
        mr = winmm.timeBeginPeriod(milliseconds)
        return mr == wintypes.MMERROR.NOERROR

    return False
