"""
Minimal OpenCL 1.2 low level ctypes API.
"""
import ctypes
from ctypes import POINTER, create_string_buffer, sizeof, c_char_p, c_char, c_size_t, c_void_p, byref
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

class cl_char(ctypes.c_int8): pass
class cl_uchar(ctypes.c_uint8): pass
class cl_short(ctypes.c_int16): pass
class cl_ushort(ctypes.c_uint16): pass
class cl_int(ctypes.c_int32): pass
class cl_uint(ctypes.c_uint32): pass
class cl_long(ctypes.c_int64): pass
class cl_ulong(ctypes.c_uint64): pass
class cl_half(ctypes.c_uint16): pass
class cl_float(ctypes.c_float): pass
class cl_double(ctypes.c_double): pass
class cl_bool(cl_uint): pass
class cl_bitfield(cl_ulong):
    def __or__(self, other):
        assert isinstance(other, self.__class__)
        return self.__class__(self.value | other.value)
    def __and__(self, other):
        assert isinstance(other, self.__class__)
        return self.__class__(self.value & other.value)
    def __xor__(self, other):
        assert isinstance(other, self.__class__)
        return self.__class__(self.value ^ other.value)
    def __not__(self):
        return self.__class__(~self.value)
    def __contains__(self, other):
        assert isinstance(other, self.__class__)
        return (self.value & other.value) == other.value
    def __hash__(self):
        return self.value.__hash__()
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.value == other.value
    def __ne__(self, other):
        return not(self == other)
    def __repr__(self):
        return f'cl_bitfield: {self.value}'

class CLERROR(IntEnum):
    SUCCESS =                                  0
    DEVICE_NOT_FOUND =                         -1
    DEVICE_NOT_AVAILABLE =                     -2
    COMPILER_NOT_AVAILABLE =                   -3
    MEM_OBJECT_ALLOCATION_FAILURE =            -4
    OUT_OF_RESOURCES =                         -5
    OUT_OF_HOST_MEMORY =                       -6
    PROFILING_INFO_NOT_AVAILABLE =             -7
    MEM_COPY_OVERLAP =                         -8
    IMAGE_FORMAT_MISMATCH =                    -9
    IMAGE_FORMAT_NOT_SUPPORTED =               -10
    BUILD_PROGRAM_FAILURE =                    -11
    MAP_FAILURE =                              -12
    MISALIGNED_SUB_BUFFER_OFFSET =             -13
    EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST = -14
    INVALID_VALUE =                            -30
    INVALID_DEVICE_TYPE =                      -31
    INVALID_PLATFORM =                         -32
    INVALID_DEVICE =                           -33
    INVALID_CONTEXT =                          -34
    INVALID_QUEUE_PROPERTIES =                 -35
    INVALID_COMMAND_QUEUE =                    -36
    INVALID_HOST_PTR =                         -37
    INVALID_MEM_OBJECT =                       -38
    INVALID_IMAGE_FORMAT_DESCRIPTOR =          -39
    INVALID_IMAGE_SIZE =                       -40
    INVALID_SAMPLER =                          -41
    INVALID_BINARY =                           -42
    INVALID_BUILD_OPTIONS =                    -43
    INVALID_PROGRAM =                          -44
    INVALID_PROGRAM_EXECUTABLE =               -45
    INVALID_KERNEL_NAME =                      -46
    INVALID_KERNEL_DEFINITION =                -47
    INVALID_KERNEL =                           -48
    INVALID_ARG_INDEX =                        -49
    INVALID_ARG_VALUE =                        -50
    INVALID_ARG_SIZE =                         -51
    INVALID_KERNEL_ARGS =                      -52
    INVALID_WORK_DIMENSION =                   -53
    INVALID_WORK_GROUP_SIZE =                  -54
    INVALID_WORK_ITEM_SIZE =                   -55
    INVALID_GLOBAL_OFFSET =                    -56
    INVALID_EVENT_WAIT_LIST =                  -57
    INVALID_EVENT =                            -58
    INVALID_OPERATION =                        -59
    INVALID_GL_OBJECT =                        -60
    INVALID_BUFFER_SIZE =                      -61
    INVALID_MIP_LEVEL =                        -62
    INVALID_GLOBAL_WORK_SIZE =                 -63
    INVALID_PROPERTY =                         -64
    INVALID_GL_SHAREGROUP_REFERENCE_KHR =      -1000
    PLATFORM_NOT_FOUND_KHR =                   -1001

class CLRESULT(cl_int):
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
            return f'CLRESULT ({str(CLERROR(self.value))})'
        except:
            return f'CLRESULT ({self.value})'
    def __repr__(self):
        return self.__str__()

class cl_platform_id(c_void_p): ...
class cl_platform_info(cl_uint): ...
class cl_device_id(c_void_p): ...
class cl_device_type(cl_bitfield): ...
class cl_device_info(cl_uint): ...
class cl_context(c_void_p): ...
class cl_context_properties(c_void_p): ...
class cl_command_queue(c_void_p): ...
class cl_command_queue_properties(cl_bitfield): ...
class cl_event(c_void_p): ...
class cl_mem(c_void_p): ...
class cl_mem_info(cl_uint): ...
class cl_mem_flags(cl_bitfield): ...
class cl_program(c_void_p): ...
class cl_program_build_info(cl_uint): ...
class cl_kernel(c_void_p): ...

# https://github.com/KhronosGroup/OpenCL-Headers/blob/master/CL/cl.h
CL_PLATFORM_PROFILE    = cl_platform_info(0x0900)
CL_PLATFORM_VERSION    = cl_platform_info(0x0901)
CL_PLATFORM_NAME       = cl_platform_info(0x0902)
CL_PLATFORM_VENDOR     = cl_platform_info(0x0903)
CL_PLATFORM_EXTENSIONS = cl_platform_info(0x0904)

CL_DEVICE_TYPE_DEFAULT     = cl_device_type( (1 << 0) )
CL_DEVICE_TYPE_CPU         = cl_device_type( (1 << 1) )
CL_DEVICE_TYPE_GPU         = cl_device_type( (1 << 2) )
CL_DEVICE_TYPE_ACCELERATOR = cl_device_type( (1 << 3) )
CL_DEVICE_TYPE_ALL         = cl_device_type( 0xFFFFFFFF )

CL_DEVICE_TYPE                = cl_device_info (0x1000)
CL_DEVICE_VENDOR_ID           = cl_device_info (0x1001)
CL_DEVICE_MAX_COMPUTE_UNITS   = cl_device_info (0x1002)
CL_DEVICE_GLOBAL_MEM_SIZE     = cl_device_info (0x101F)
CL_DEVICE_NAME                = cl_device_info (0x102B)
CL_DEVICE_VERSION             = cl_device_info (0x102F)
CL_DEVICE_MAX_MEM_ALLOC_SIZE  = cl_device_info (0x1010)
CL_DEVICE_MAX_WORK_GROUP_SIZE = cl_device_info (0x1004)
CL_DRIVER_VERSION             = cl_device_info (0x102D)
CL_DEVICE_EXTENSIONS          = cl_device_info (0x1030)

# cl_mem_flags
CL_MEM_READ_WRITE     = cl_mem_flags( (1 << 0) )
CL_MEM_WRITE_ONLY     = cl_mem_flags( (1 << 1) )
CL_MEM_READ_ONLY      = cl_mem_flags( (1 << 2) )
CL_MEM_USE_HOST_PTR   = cl_mem_flags( (1 << 3) )
CL_MEM_ALLOC_HOST_PTR = cl_mem_flags( (1 << 4) )
CL_MEM_COPY_HOST_PTR  = cl_mem_flags( (1 << 5) )

# cl_mem_info
CL_MEM_SIZE = cl_mem_info(0x1102)

# cl_program_build_info
CL_PROGRAM_BUILD_STATUS  = cl_program_build_info(0x1181)
CL_PROGRAM_BUILD_OPTIONS = cl_program_build_info(0x1182)
CL_PROGRAM_BUILD_LOG     = cl_program_build_info(0x1183)


@dll_import('OpenCL')
def clGetPlatformIDs (num_entries : cl_uint, platforms : POINTER(cl_platform_id), num_platforms : POINTER(cl_uint) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clGetPlatformInfo (platform : cl_platform_id, param_name : cl_platform_info, param_value_size : c_size_t, param_value : c_void_p, param_value_size_ret : POINTER(c_size_t)) -> CLRESULT: ...

@dll_import('OpenCL')
def clGetDeviceIDs (platform : cl_platform_id, device_type : cl_device_type, num_entries : cl_uint, devices : POINTER(cl_device_id), num_devices : POINTER(cl_uint)) -> CLRESULT: ...

@dll_import('OpenCL')
def clGetDeviceInfo(device : cl_device_id, param_name : cl_device_info, param_value_size : c_size_t, param_value : c_void_p, param_value_size_ret : POINTER(c_size_t)) -> CLRESULT: ...

@dll_import('OpenCL')
def clCreateContext(properties : cl_context_properties, num_devices : cl_uint,  devices : POINTER(cl_device_id), pfn_notify : c_void_p, user_data : c_void_p, errcode_ret : POINTER(CLRESULT) ) -> cl_context: ...

@dll_import('OpenCL')
def clReleaseContext(context : cl_context) -> CLRESULT: ...

@dll_import('OpenCL')
def clCreateCommandQueue(context : cl_context, device : cl_device_id, properties : cl_command_queue_properties, errcode_ret : POINTER(CLRESULT) ) -> cl_command_queue: ...

@dll_import('OpenCL')
def clReleaseCommandQueue(command_queue : cl_command_queue) -> CLRESULT: ...

@dll_import('OpenCL')
def clFinish(command_queue : cl_command_queue) -> CLRESULT: ...

@dll_import('OpenCL')
def clWaitForEvents(num_events : cl_uint, event_list : POINTER(cl_event) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clReleaseEvent(event : cl_event) -> CLRESULT: ...

@dll_import('OpenCL')
def clCreateBuffer(context : cl_context, flags : cl_mem_flags, size : c_size_t, host_ptr : c_void_p, errcode_ret : POINTER(CLRESULT) ) -> cl_mem: ...

@dll_import('OpenCL')
def clGetMemObjectInfo(memobj : cl_mem, param_name : cl_mem_info, param_value_size : c_size_t, param_value : c_void_p, param_value_size_ret : POINTER(c_size_t) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clReleaseMemObject(memobj : cl_mem) -> CLRESULT: ...

@dll_import('OpenCL')
def clEnqueueReadBuffer (command_queue : cl_command_queue, buffer : cl_mem, blocking_read : cl_bool, offset : c_size_t, cb : c_size_t, ptr : c_void_p, num_events_in_wait_list : cl_uint, event_wait_list : POINTER(cl_event), event : POINTER(cl_event) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clEnqueueWriteBuffer (command_queue : cl_command_queue, buffer : cl_mem, blocking_write : cl_bool, offset : c_size_t, size : c_size_t, ptr : c_void_p, num_events_in_wait_list : cl_uint, event_wait_list : POINTER(cl_event), event : POINTER(cl_event) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clEnqueueCopyBuffer (command_queue : cl_command_queue, src_buffer : cl_mem, dst_buffer : cl_mem, src_offset : c_size_t, dst_offset : c_size_t, cb : c_size_t, num_events_in_wait_list : cl_uint, event_wait_list : POINTER(cl_event), event : cl_event) -> CLRESULT: ...

@dll_import('OpenCL')
def clEnqueueFillBuffer (command_queue : cl_command_queue, buffer : cl_mem, pattern : c_void_p, pattern_size : c_size_t, offset : c_size_t, size : c_size_t, num_events_in_wait_list : cl_uint, event_wait_list : POINTER(cl_event), event : POINTER(cl_event) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clCreateProgramWithSource (context : cl_context, count : cl_uint, strings : POINTER(c_char_p), lengths : POINTER(c_size_t), errcode_ret : POINTER(CLRESULT) ) -> cl_program: ...

@dll_import('OpenCL')
def clReleaseProgram (program : cl_program) -> CLRESULT: ...

@dll_import('OpenCL')
def clBuildProgram (program : cl_program, num_devices : cl_uint, device_list : POINTER(cl_device_id), options : c_char_p, pfn_notify : c_void_p, user_data : c_void_p) -> CLRESULT: ...

@dll_import('OpenCL')
def  clGetProgramBuildInfo (program : cl_program, device : cl_device_id, param_name : cl_program_build_info, param_value_size : c_size_t, param_value : c_void_p, param_value_size_ret : POINTER(c_size_t) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clCreateKernelsInProgram (program : cl_program, num_kernels : cl_uint, kernels : POINTER(cl_kernel), num_kernels_ret : POINTER(cl_uint) ) -> CLRESULT: ...

@dll_import('OpenCL')
def clReleaseKernel (program : cl_kernel) -> CLRESULT: ...

@dll_import('OpenCL')
def clSetKernelArg (kernel : cl_kernel, arg_index : cl_uint, arg_size : c_size_t, arg_value : c_void_p) -> CLRESULT: ...

@dll_import('OpenCL')
def clEnqueueNDRangeKernel (command_queue : cl_command_queue, kernel : cl_kernel, work_dim : cl_uint, global_work_offset : POINTER(c_size_t), global_work_size : POINTER(c_size_t), local_work_size : POINTER(c_size_t), num_events_in_wait_list : cl_uint, event_wait_list : POINTER(cl_event), event : POINTER(cl_event) ) -> CLRESULT: ...
