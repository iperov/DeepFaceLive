import ctypes
import uuid
from ctypes import (POINTER, WINFUNCTYPE, byref, c_byte, c_int64,
                    c_longlong, c_size_t, c_ubyte, c_uint, c_uint32, c_ulong,
                    c_void_p, c_wchar)
from ctypes.util import find_library
from enum import IntEnum

dlls_by_name = {}

def dll_import(dll_name):
    dll = dlls_by_name.get(dll_name, None)
    if dll is None:
        try:
            dll = ctypes.cdll.LoadLibrary(find_library(dll_name))
        except:
            pass
        if dll is None:
            raise RuntimeError(f'Unable to load {dll_name} library.')
        dlls_by_name[dll_name] = dll
    
    def decorator(func):
        dll_func = getattr(dll, func.__name__)
        anno = list(func.__annotations__.values())
        dll_func.argtypes = anno[:-1]
        dll_func.restype = anno[-1]
        def wrapper(*args):
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
        
              
class GUID (ctypes.Structure):
    _fields_ = [('data', c_ubyte * 16)]
    def __init__(self, hexstr=None):
        super().__init__()
        self.data[:] = uuid.UUID(hexstr).bytes_le
IID = GUID
REFIID = POINTER(IID)
REFGUID = POINTER(GUID)



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


# class COMObject(c_void_p):
#     """
#     base class for COM objects
    
#     you should implement _vf_table in every subclass
#     """
#     def _vf_table(): return dict()
        
#     def _get_vf_func(self, name):
#         """
#         returns function from vf table by name
#         """
#         if self.value is None:
#             raise Exception(f'COMObject {self} was not assigned.')
        
#         vf_proto_cls = self.__class__
        
#         vf = getattr(vf_proto_cls, '_vf', None)
#         if vf is None:
#             vf = {}
            
#             hierarchy = []
#             while vf_proto_cls != COMObject:
#                 hierarchy.insert(0, vf_proto_cls)
#                 vf_proto_cls = vf_proto_cls.__bases__[0]
                
#             func_id = 0
#             for vf_proto_cls in hierarchy:
#                 for func_name, func_type in vf_proto_cls._vf_table().items():
#                     if func_name in vf:
#                         raise Exception(f'Function duplicate {func_name} in {self}')
#                     vf[func_name] = (func_id, func_type)
#                     func_id += 1
#             setattr(vf_proto_cls, '_vf', vf)
        
#         func_id, func_type = vf[name]
#         vf_table = ct.cast( c_void_p( ct.cast(self, POINTER(c_void_p))[0] ), POINTER(c_void_p))
#         return func_type(vf_table[func_id])    

# class IUnknown(COMObject):
#     def QueryInterface(self, iid : REFIID, out_IUnknown : POINTER(c_void_p)) -> HRESULT: 
#         return self._get_vf_func('QueryInterface')(self, iid, out_IUnknown)
    
#     def AddRef(self) -> c_ulong:  
#         return self._get_vf_func('AddRef')(self)
        
#     def Release(self) -> c_ulong: 
#         return self._get_vf_func('Release')(self)
        
#     IID = GUID('00000000-0000-0000-C000-000000000046')
    
#     def _vf_table(): return dict(
#         QueryInterface      = WINFUNCTYPE(HRESULT, IUnknown, REFIID, POINTER(IUnknown) ),
#         AddRef              = WINFUNCTYPE(c_ulong, IUnknown),
#         Release             = WINFUNCTYPE(c_ulong, IUnknown), 
#         )
    

#     def query_interface(self, iid : IID) -> 'IUnknown':
#         out_IUnknown = IUnknown()
#         hr = self.QueryInterface(iid, out_IUnknown)
#         if hr == ERROR.SUCCESS:
#             return out_IUnknown
#         return None
       
       
# class COMBase(c_void_p): ...
    

# def com_class(cls_obj):
#     virtual_idx = 0
    
#     # Determine virtuals count from parent class
#     parent = cls_obj.__bases__[0]
#     if parent != COMBase:
#         virtual_idx = parent._virtuals_count
            
#     # Walk through all virtuals and assign virtual idx
#     for key, value in cls_obj.__dict__.items():
#         _virtual_idx = getattr(value, '_virtual_idx', None)
#         if _virtual_idx is not None:
#             value._virtual_idx = virtual_idx
#             virtual_idx += 1
            
#     cls_obj._virtuals_count = virtual_idx
#     return cls_obj
    

# @com_class
# class IUnknown(COMBase):

#     @virtual
#     def QueryInterface(self, refiid : REFIID, pIUnknown : POINTER(c_void_p) ) -> HRESULT: ...
    
#     @virtual
#     def AddRef(self : COMBase) -> c_ulong: ...
        
#     @virtual
#     def Release(self : COMBase) -> c_ulong: ...

# def virtual(func):
#     func_type = None
    
#     def wrapper(this, *args):
#         if wrapper._functype is None:
#             x = wrapper._virtual_idx
#             anno = list(func.__annotations__.values())
#             wrapper._functype = WINFUNCTYPE(anno[-1], *anno[:-1])
            
#         vf_table = ct.cast( c_void_p( ct.cast(this, POINTER(c_void_p))[0] ), POINTER(c_void_p))
#         real_func = wrapper._functype( vf_table[wrapper._virtual_idx] )
        
        
#         import code
#         code.interact(local=dict(globals(), **locals()))
        
        
        
#         return real_func(this, *args)
#     wrapper._func = func
#     wrapper._functype = None
#     wrapper._virtual_idx = -1
#     return wrapper
