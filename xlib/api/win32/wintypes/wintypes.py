import ctypes
import uuid
from ctypes import (POINTER, WINFUNCTYPE, c_char_p, c_int16, c_int32, c_float, c_double, c_uint8,
                    c_int64, c_int8, c_size_t, c_ubyte, c_uint, c_uint16,
                    c_uint32, c_uint64, c_ulong, c_void_p, c_wchar_p)
from ctypes.util import find_library
from enum import IntEnum

dlls_by_name = {}

def dll_import(dll_name):
    """

    always annotate return type even if it is None !
    """

    dll = dlls_by_name.get(dll_name, None)
    if dll is None:
        try:
            dll = ctypes.cdll.LoadLibrary(find_library(dll_name))
        except:
            pass

        dlls_by_name[dll_name] = dll

    def decorator(func):
        if dll is not None:
            dll_func = getattr(dll, func.__name__)
            anno = list(func.__annotations__.values())
            dll_func.argtypes = anno[:-1]
            dll_func.restype = anno[-1]
        else:
            dll_func = None

        def wrapper(*args):
            if dll_func is None:
                raise RuntimeError(f'Unable to load {dll_name} library.')
            return dll_func(*args)
        return wrapper
    return decorator


def interface(cls_obj):
    """
    Decorator for COM interfaces.

    First declarations must be a virtual functions.

    IID = GUID('') declares the end of virtual functions declarations
    """
    virtual_idx = None
    parent_cls_obj = cls_obj
    while True:
        parent_cls_obj = parent_cls_obj.__bases__[0]
        if parent_cls_obj is object:
            break
        virtual_idx = getattr(parent_cls_obj, '_virtual_idx', None)
        if virtual_idx is not None:
            break
    if virtual_idx is None:
        virtual_idx = 0

    if 'IID' not in list(cls_obj.__dict__.keys()):
        raise Exception(f'class {cls_obj} declared as @interface, but no IID variable found.')

    for key, value in list(cls_obj.__dict__.items()):
        if len(key) >= 2 and key[0:2] == '__':
            continue
        if key == 'IID':
            break

        anno_list = list(value.__annotations__.values())

        func_type = WINFUNCTYPE(anno_list[-1], c_void_p, *anno_list[:-1])
        def wrapper(self, *args, _key=key, _virtual_idx=virtual_idx, _func_type=func_type):
            func = getattr(self, '_func_'+_key, None)
            if func is None:
                if self.value is None:
                    raise Exception(f'{self} is not initialized.')

                vf_table = ctypes.cast( c_void_p( ctypes.cast(self, POINTER(c_void_p))[0] ), POINTER(c_void_p))
                func = _func_type(vf_table[_virtual_idx])
                setattr(self, '_func_'+key, func)
            return func(self, *args)

        setattr(cls_obj, key, wrapper)
        virtual_idx += 1

    cls_obj._virtual_idx = virtual_idx
    return cls_obj


class ERROR(IntEnum):
    # https://raw.githubusercontent.com/tpn/winsdk-10/master/Include/10.0.14393.0/shared/winerror.h
    SUCCESS = 0
    INVALID_FUNCTION = 1
    E_NOINTERFACE = 0x80004002

    DXGI_ERROR_NOT_FOUND = 0x887A0002

class MMERROR(IntEnum):
    # http://pinvoke.net/default.aspx/winmm/MMRESULT.html
    NOERROR = 0
    ERROR = 1

class MMRESULT(c_ulong):
    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        try:
            return f'MMRESULT ({str(MMERROR(self.value))})'
        except:
            return f'MMRESULT ({self.value})'
    def __repr__(self):
        return self.__str__()

class HRESULT(c_ulong):
    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        try:
            return f'HRESULT ({str(ERROR(self.value))})'
        except:
            return f'HRESULT ({self.value})'
    def __repr__(self):
        return self.__str__()

class HANDLE(c_void_p):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'HANDLE ({self.value})'
    def __repr__(self):
        return self.__str__()


class BOOL(c_size_t):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.value != 0) == (other.value != 0)
        elif isinstance(other, bool):
            return (self.value != 0) == other
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'BOOL ({self.value != 0})'
    def __repr__(self):
        return self.__str__()

class CHAR(c_int8):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'CHAR ({self.value})'
    def __repr__(self):
        return self.__str__()

class BYTE(c_uint8):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'BYTE ({self.value})'
    def __repr__(self):
        return self.__str__()

class SHORT(c_int16):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'SHORT ({self.value})'
    def __repr__(self):
        return self.__str__()

class USHORT(c_uint16):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'USHORT ({self.value})'
    def __repr__(self):
        return self.__str__()

class LONG(c_int32):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'LONG ({self.value})'
    def __repr__(self):
        return self.__str__()

class ULONG(c_uint32):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'ULONG ({self.value})'
    def __repr__(self):
        return self.__str__()

class INT(c_int32):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'INT ({self.value})'
    def __repr__(self):
        return self.__str__()

class UINT(c_uint32):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'UINT ({self.value})'
    def __repr__(self):
        return self.__str__()

class WORD(c_uint16):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'WORD ({self.value})'
    def __repr__(self):
        return self.__str__()

class DWORD(c_uint):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'DWORD ({self.value})'
    def __repr__(self):
        return self.__str__()

class LARGE_INTEGER(c_int64):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'LARGE_INTEGER ({self.value})'
    def __repr__(self):
        return self.__str__()

class LONGLONG(c_int64):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'LONGLONG ({self.value})'
    def __repr__(self):
        return self.__str__()

class ULONGLONG(c_uint64):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'ULONGLONG ({self.value})'
    def __repr__(self):
        return self.__str__()

class ULARGE_INTEGER(c_uint64):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'ULARGE_INTEGER ({self.value})'
    def __repr__(self):
        return self.__str__()

class FLOAT(c_float):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'FLOAT ({self.value})'
    def __repr__(self):
        return self.__str__()

class DOUBLE(c_double):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'DOUBLE ({self.value})'
    def __repr__(self):
        return self.__str__()

class PVOID(c_void_p):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return self.value.__hash__()
    def __str__(self):
        return f'PVOID ({self.value})'
    def __repr__(self):
        return self.__str__()

class GUID (ctypes.Structure):
    _fields_ = [('data', c_ubyte * 16)]
    def __init__(self, hexstr=None):
        super().__init__()
        self.data[:] = uuid.UUID(hexstr).bytes_le

class CSTR(c_char_p):
    def __init__(self, s : str):
        super().__init__(s.encode('utf-8'))

class CLSID(GUID): ...
class LPCOLESTR(c_wchar_p): ...
class BSTR(c_wchar_p): ...

IID = GUID
REFIID = POINTER(IID)
REFGUID = POINTER(GUID)
REFCLSID = POINTER(CLSID)
#LPOLESTR = POINTER(OLESTR)

@interface
class IUnknown(c_void_p):
    def QueryInterface(self, iid : REFIID, out_IUnknown : POINTER(c_void_p)) -> HRESULT: ...
    def AddRef(self) -> c_ulong: ...
    def Release(self) -> c_ulong: ...
    IID = GUID('00000000-0000-0000-C000-000000000046')

    def query_interface(self, iid : IID) -> 'IUnknown':
        out_IUnknown = IUnknown()
        hr = self.QueryInterface(iid, out_IUnknown)
        if hr == ERROR.SUCCESS:
            return out_IUnknown
        return None


class VARTYPE(SHORT):
    VT_EMPTY = 0
    VT_NULL = 1
    VT_I2 = 2
    VT_I4 = 3
    VT_R4 = 4
    VT_R8 = 5
    VT_CY = 6
    VT_DATE = 7
    VT_BSTR = 8
    VT_DISPATCH = 9
    VT_ERROR = 10
    VT_BOOL = 11
    VT_VARIANT = 12
    VT_UNKNOWN = 13
    VT_DECIMAL = 14
    VT_I1 = 16
    VT_UI1 = 17
    VT_UI2 = 18
    VT_UI4 = 19
    VT_I8 = 20
    VT_UI8 = 21
    VT_INT = 22
    VT_UINT = 23
    VT_VOID = 24
    VT_HRESULT = 25
    VT_PTR = 26
    VT_SAFEARRAY = 27
    VT_CARRAY = 28
    VT_USERDEFINED = 29
    VT_LPSTR = 30
    VT_LPWSTR = 31
    VT_RECORD = 36
    VT_INT_PTR = 37
    VT_UINT_PTR = 38
    VT_FILETIME = 64
    VT_BLOB = 65
    VT_STREAM = 66
    VT_STORAGE = 67
    VT_STREAMED_OBJECT = 68
    VT_STORED_OBJECT = 69
    VT_BLOB_OBJECT = 70
    VT_CF = 71
    VT_CLSID = 72
    VT_VERSIONED_STREAM = 73
    VT_BSTR_BLOB = 0xfff
    VT_VECTOR = 0x1000
    VT_ARRAY = 0x2000
    VT_BYREF = 0x4000
    VT_RESERVED = 0x8000
    VT_ILLEGAL = 0xffff
    VT_ILLEGALMASKED = 0xfff
    VT_TYPEMASK = 0xff

class _VARIANT_RECORD(ctypes.Structure):
    _fields_ = [ ('pvRecord', PVOID),
                 ('pRecInfo', IUnknown ) ] #IRecordInfo

class _VARIANT_NAME_3(ctypes.Union):
    _fields_ = [ ('llVal', LONGLONG),
                 ('lVal', LONG),
                 ('bVal', BYTE),
                 ('iVal', SHORT),
                 ('fltVal', FLOAT),
                 ('dblVal', DOUBLE),
                    #VARIANT_BOOL boolVal;
                    #VARIANT_BOOL __OBSOLETE__VARIANT_BOOL;
                    #SCODE        scode;
                    #CY           cyVal;
                    #DATE         date;
                 ('bstrVal', BSTR),
                 ('punkVal', IUnknown),
                    #IDispatch    *pdispVal;
                    #SAFEARRAY    *parray;
                 ('pbVal', POINTER(BYTE)),
                 ('piVal', POINTER(SHORT)),
                 ('plVal', POINTER(LONG)),
                 ('pllVal', POINTER(LONGLONG)),
                 ('pfltVal', POINTER(FLOAT)),
                 ('pdblVal', POINTER(DOUBLE)),
                    # VARIANT_BOOL *pboolVal;
                    # VARIANT_BOOL *__OBSOLETE__VARIANT_PBOOL;
                    # SCODE        *pscode;
                    # CY           *pcyVal;
                    # DATE         *pdate;
                 ('pbstrVal', POINTER(BSTR) ),
                 ('ppunkVal', POINTER(IUnknown) ),
                    # IDispatch    **ppdispVal;
                    # SAFEARRAY    **pparray;
                    # VARIANT      *pvarVal;
                 ('byref', PVOID),
                 ('cVal', CHAR),
                 ('uiVal', USHORT),
                 ('ulVal', ULONG),
                 ('ullVal', ULONGLONG),
                 ('intVal', INT),
                 ('uintVal', UINT),
                    #DECIMAL      *pdecVal;
                 ('pcVal', POINTER(CHAR)),
                 ('puiVal', POINTER(USHORT)),
                 ('pulVal', POINTER(ULONG)),
                 ('pullVal', POINTER(ULONGLONG)),
                 ('pintVal', POINTER(INT)),
                 ('puintVal', POINTER(UINT)),

                 ('record', _VARIANT_RECORD ),
                ]

class VARIANT(ctypes.Structure):
    _fields_ = [('vt', VARTYPE ),
                ('wReserved1', WORD),
                ('wReserved2', WORD),
                ('wReserved3', WORD),
                ('value', _VARIANT_NAME_3),
               ]
    def __init__(self):
        """
        by default initialized to VT_EMPTY
        """

        self.vt : VARTYPE = VARTYPE.VT_EMPTY
        #self.wReserved1 : WORD = WORD()
        #self.wReserved2 : WORD = WORD()
        #self.wReserved3 : WORD = WORD()
        #self.value : _VARIANT_NAME_3 = _VARIANT_NAME_3()
        super().__init__()

    def __repr__(self): return self.__str__()
    def __str__(self):
        return f'VARIANT object: { self.vt }'



