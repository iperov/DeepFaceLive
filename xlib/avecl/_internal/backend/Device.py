import random
from collections import deque
from typing import List, Union

import numpy as np

from . import OpenCL as CL
from .Buffer import Buffer
from .DeviceInfo import DeviceInfo
from .Kernel import Kernel

_np_dtype_to_cl = { np.uint8:   CL.cl_uchar,
                    np.int8:    CL.cl_char,
                    np.uint16:  CL.cl_ushort,
                    np.int16:   CL.cl_short,
                    np.uint32:  CL.cl_uint,
                    np.int32:   CL.cl_int,
                    np.uint64:  CL.cl_ulong,
                    np.int64:   CL.cl_long,
                    np.float16: CL.cl_half,
                    np.float32: CL.cl_float}

_opencl_device_ids = None
_default_device = None
_devices = {}

class Device:
    """
    Represents physical TensorCL device
    """

    def __init__(self, device_info : DeviceInfo, **kwargs):
        if kwargs.get('_check', None) is None:
            raise Exception('You should not to create Device from constructor. Use get_device()')

        self._cached_data = {}      # cached data (per device) by key
        self._pooled_buffers = {}   # Pool of cached device buffers.
        self._cached_kernels = {} # compiled kernels by key
        self._ctx_q = None          # CL command queue
        self._ctx = None            # CL context

        self._target_memory_usage = 0

        self._total_memory_allocated = 0
        self._total_buffers_allocated = 0
        self._total_memory_pooled = 0
        self._total_buffers_pooled = 0

        self._device_info = device_info
        self._device_id = _get_opencl_device_ids()[device_info.get_index()]

    def __del__(self):
        self.cleanup()

    def __eq__(self, other):
        if self is not None and other is not None and isinstance(self, Device) and isinstance(other, Device):
            return self._device_id.value == other._device_id.value
        return False

    def __hash__(self):
        return self._device_id.value

    def _get_ctx(self) -> CL.cl_context:
        # Create OpenCL context on demand
        if self._ctx is None:
            clr = CL.CLRESULT()
            ctx = CL.clCreateContext( None, 1, (CL.cl_device_id * 1)( self._device_id ), None, None, clr)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception('Unable to create OpenCL context.')
            self._ctx = ctx
        return self._ctx

    def _get_ctx_q(self) -> CL.cl_command_queue:
        # Create CommandQueue on demand
        if self._ctx_q is None:
            clr = CL.CLRESULT()
            ctx_q = CL.clCreateCommandQueue(self._get_ctx(), self._device_id, CL.cl_command_queue_properties(0), clr)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception('Unable to create OpenCL CommandQueue.')
            self._ctx_q = ctx_q
        return self._ctx_q

    def _compile_kernel(self, key, kernel_text) -> CL.cl_kernel:
        """
        compile or get cached kernel
        """

        compiled_krn, prog = self._cached_kernels.get(key, (None, None) )
        if compiled_krn is None:
            clr = CL.CLRESULT()
            prog = CL.clCreateProgramWithSource(self._get_ctx(), 1, CL.c_char_p(kernel_text.encode()), None, clr )
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clCreateProgramWithSource error {clr}, with kernel_text:\n{kernel_text}')

            clr = CL.clBuildProgram(prog, 1, (CL.cl_device_id*1)(self._device_id), CL.c_char_p('-cl-std=CL1.2 -cl-single-precision-constant'.encode()), None, None  )
            if clr != CL.CLERROR.SUCCESS:
                build_log_size = CL.c_size_t()
                clr = CL.clGetProgramBuildInfo(prog, self._device_id, CL.CL_PROGRAM_BUILD_LOG, 0, None, CL.byref(build_log_size) )
                if clr != CL.CLERROR.SUCCESS:
                    raise Exception(f'clGetProgramBuildInfo,error: {clr}')

                build_log = CL.create_string_buffer(build_log_size.value)
                clr = CL.clGetProgramBuildInfo(prog, self._device_id, CL.CL_PROGRAM_BUILD_LOG, build_log_size.value, build_log, None )
                if clr != CL.CLERROR.SUCCESS:
                    raise Exception(f'clGetProgramBuildInfo error: {clr}')

                build_log = str(build_log.value, 'utf-8')
                raise Exception(f'clBuildProgram error:\n\n{build_log}')

            num_kernels = CL.cl_uint()
            clr = CL.clCreateKernelsInProgram(prog, 0, None, CL.byref(num_kernels))
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clCreateKernelsInProgram error: {clr}')

            if num_kernels.value != 1:
                raise Exception(f'Kernel must contain only one __kernel:\n\n{kernel_text}')

            kernels = (CL.cl_kernel * num_kernels.value)()
            clr = CL.clCreateKernelsInProgram(prog, num_kernels.value, kernels, None)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clCreateKernelsInProgram error: {clr}')

            compiled_krn = kernels[0]
            self._cached_kernels[key] = (compiled_krn, prog)

        return compiled_krn

    def _cl_mem_alloc(self, size) -> CL.cl_mem:
        self._keep_target_memory_usage()

        clr = CL.CLRESULT()
        mem = CL.clCreateBuffer(self._get_ctx(), CL.CL_MEM_READ_WRITE, size, None, clr)
        if clr == CL.CLERROR.SUCCESS:
            # Fill one byte to check memory availability
            ev = CL.cl_event()
            clr = CL.clEnqueueFillBuffer (self._get_ctx_q(), mem, (CL.c_char * 1)(), 1, 0, 1, 0, None, ev )
            if clr == CL.CLERROR.SUCCESS:
                CL.clReleaseEvent(ev)
                self._total_memory_allocated += size
                self._total_buffers_allocated += 1
                return mem
        return None

    def _cl_mem_free(self, mem : CL.cl_mem):
        size = CL.c_size_t()
        clr = CL.clGetMemObjectInfo(mem, CL.CL_MEM_SIZE, CL.sizeof(size), CL.byref(size), None )
        if clr != CL.CLERROR.SUCCESS:
            raise Exception(f'clGetMemObjectInfo error: {clr}')
        size = size.value

        self._total_memory_allocated -= size
        self._total_buffers_allocated -= 1
        clr = CL.clReleaseMemObject(mem)
        if clr != CL.CLERROR.SUCCESS:
            raise Exception(f'clReleaseMemObject error: {clr}')

    def _cl_mem_pool_alloc(self, size):
        """
        allocate or get cl_mem from pool
        """
        self._keep_target_memory_usage()

        pool = self._pooled_buffers

        # First try to get pooled buffer
        ar = pool.get(size, None)
        if ar is not None and len(ar) != 0:
            mem = ar.pop()
            self._total_memory_pooled -= size
            self._total_buffers_pooled -= 1
        else:
            # No pooled buffer, try to allocate new
            while True:
                mem = self._cl_mem_alloc(size)
                if mem is None:
                    # MemoryError.
                    if not self._release_random_pooled_buffers():
                        raise Exception(f'Unable to allocate {size // 1024**2}Mb on {self.get_description()}')
                    continue
                break

        return mem

    def _cl_mem_pool_free(self, mem : CL.cl_mem):
        """
        Put cl_mem to pool for reuse in future.
        """
        size = CL.c_size_t()
        clr = CL.clGetMemObjectInfo(mem, CL.CL_MEM_SIZE, CL.sizeof(size), CL.byref(size), None )
        if clr != CL.CLERROR.SUCCESS:
            raise Exception(f'clGetMemObjectInfo error: {clr}')
        size = size.value

        pool = self._pooled_buffers
        ar = pool.get(size, None)
        if ar is None:
            ar = pool[size] = deque()
        ar.append(mem)

        self._total_memory_pooled += size
        self._total_buffers_pooled += 1

    def _release_random_pooled_buffers(self) -> bool:
        """
        remove random 25% of pooled boofers

        returns True if something was released
        """
        pool = self._pooled_buffers
        mems = [ (k,x) for k in pool.keys() for x in pool[k]  ]

        if len(mems) != 0:
            mems = random.sample(mems, max(1,int(len(mems)*0.25)) )
            for k, mem in mems:
                self._cl_mem_free(mem)
                pool[k].remove(mem)
        return len(mems) != 0

    def _keep_target_memory_usage(self):
        targ = self._target_memory_usage
        if targ != 0 and self.get_total_allocated_memory() >= targ:
            self.cleanup_cached_kernels()
            self._release_random_pooled_buffers()

    def __str__(self):
        return self.get_description()

    def __repr__(self):
        return f'{self.__class__.__name__} object: ' + self.__str__()

    def clear_pooled_memory(self):
        """
        frees pooled memory
        """

        pool = self._pooled_buffers
        for size_key in pool.keys():
            for mem in pool[size_key]:
                self._cl_mem_free(mem)
        self._pooled_buffers = {}
        self._total_memory_pooled = 0
        self._total_buffers_pooled = 0

    def cleanup_cached_kernels(self):
        for kernel, prog in self._cached_kernels.values():
            clr = CL.clReleaseKernel(kernel)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clReleaseKernel error: {clr}')

            clr = CL.clReleaseProgram(prog)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clReleaseProgram error: {clr}')
        self._cached_kernels = {}

    def cleanup(self):
        """
        Frees all resources from this Device.
        """
        self._cached_data = {}

        self.clear_pooled_memory()

        if self._total_memory_allocated != 0:
            raise Exception('Unable to cleanup CLDevice, while not all Buffers are deallocated.')

        self.cleanup_cached_kernels()

        if self._ctx_q is not None:
            clr = CL.clReleaseCommandQueue(self._ctx_q)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clReleaseCommandQueue error: {clr}')
            self._ctx_q = None

        if self._ctx is not None:
            clr = CL.clReleaseContext(self._ctx)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clReleaseContext error: {clr}')
            self._ctx = None

    def get_cached_data(self, key):
        return self._cached_data.get(key, None)

    def get_description(self) -> str:
        return f"{self._device_info.get_name()} [{(self._device_info.get_total_memory() / 1024**3) :.3}Gb]"

    def get_total_allocated_memory(self):
        """
        get total bytes of used and pooled memory
        """
        return self._total_memory_allocated

    def set_cached_data(self, key, value):
        """
        All cached data will be freed with cleanup()
        """
        self._cached_data[key] = value

    def set_target_memory_usage(self, mb : int):
        """
        keep memory usage at specified position

        when total allocated memory reached the target and new allocation is performing,
        random pooled memory will be freed
        """
        self._target_memory_usage = mb*1024*1024

    def print_stat(self):
        s = f'''
Total memory allocated:  {self._total_memory_allocated}
Total buffers allocated: {self._total_buffers_allocated}
Total memory pooled:     {self._total_memory_pooled}
Total buffers pooled:    {self._total_buffers_pooled}
N of compiled kernels:   {len(self._cached_kernels)}
N of cacheddata:         {len(self._cached_data)}
'''
        print(s)

    def run_kernel(self, kernel : Kernel, *args, global_shape=None, local_shape=None, global_shape_offsets=None, wait=False):
        """
        Run kernel on Device

        Arguments

            *args           arguments will be passed to OpenCL kernel
                            allowed types:

                            Buffer
                            np single value

            global_shape(None)  tuple of ints, up to 3 dims
                                amount of parallel kernel executions.
                                in OpenCL kernel,
                                id can be obtained via get_global_id(dim)

            local_shape(None)   tuple of ints, up to 3 dims
                                specifies local groups of every dim of global_shape.
                                in OpenCL kernel,
                                id can be obtained via get_local_id(dim)

            global_shape_offsets(None)  tuple of ints
                                        offsets for global_shape

            wait(False)     wait execution to complete
        """
        if global_shape is None:
            global_shape = kernel.get_global_shape()
        if global_shape is None:
            raise ValueError('global_shape must be defined.')

        work_dim = len(global_shape)
        global_shape_ar = (CL.c_size_t*work_dim)()
        for i,v in enumerate(global_shape):
            global_shape_ar[i] = v

        local_shape_ar = None
        if local_shape is None:
            local_shape = kernel.get_local_shape()
        if local_shape is not None:
            if len(local_shape) != work_dim:
                raise ValueError('len of local_shape must match global_shape')

            local_shape_ar = (CL.c_size_t*work_dim)()
            for i,v in enumerate(local_shape):
                local_shape_ar[i] = v


        global_shape_offsets_ar = None
        if global_shape_offsets is not None:
            if len(global_shape_offsets) != work_dim:
                raise ValueError('len of global_shape_offsets must match global_shape')

            global_shape_offsets_ar = (CL.c_size_t*work_dim)()
            for i,v in enumerate(local_shape):
                global_shape_offsets_ar[i] = v

        krn_args = []
        for i, arg in enumerate(args):
            if isinstance(arg, Buffer):
                arg = arg.get_cl_mem()
            else:
                cl_type = _np_dtype_to_cl.get(arg.__class__, None)
                if cl_type is None:
                    raise ValueError(f'Cannot convert type {arg.__class__} to OpenCL type.')
                arg = cl_type(arg)
            krn_args.append(arg)

        ckernel = self._compile_kernel(kernel, kernel.get_kernel_text())

        for i, arg in enumerate(krn_args):
            clr = CL.clSetKernelArg(ckernel, i, CL.sizeof(arg), CL.byref(arg))
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clSetKernelArg error: {clr}')

        ev = CL.cl_event() if wait else None

        clr = CL.clEnqueueNDRangeKernel(self._get_ctx_q(), ckernel, work_dim, global_shape_offsets_ar, global_shape_ar, local_shape_ar, 0, None, ev)
        if clr != CL.CLERROR.SUCCESS:
            raise Exception(f'clEnqueueNDRangeKernel error: {clr}')

        if wait:
            CL.clWaitForEvents(1, (CL.cl_event*1)(ev) )
            CL.clReleaseEvent(ev)

    def wait(self):
        """
        Wait to finish all queued operations on this Device
        """
        clr = CL.clFinish(self._get_ctx_q())
        if clr != CL.CLERROR.SUCCESS:
            raise Exception(f'clFinish error: {clr}')


def _get_opencl_device_ids() -> List[CL.cl_device_id]:
    global _opencl_device_ids
    if _opencl_device_ids is None:
        _opencl_device_ids = []
        device_types = CL.CL_DEVICE_TYPE_CPU | CL.CL_DEVICE_TYPE_ACCELERATOR | CL.CL_DEVICE_TYPE_GPU

        while True:
            num_platforms = CL.cl_uint()
            if CL.clGetPlatformIDs(0, None, num_platforms) != CL.CLERROR.SUCCESS or \
                num_platforms.value == 0:
                break

            platforms = (CL.cl_platform_id * num_platforms.value) ()
            if CL.clGetPlatformIDs(num_platforms.value, platforms, None) != CL.CLERROR.SUCCESS:
                break

            for i_platform in range(num_platforms.value):
                platform = platforms[i_platform]
                num_devices = CL.cl_uint(0)
                if CL.clGetDeviceIDs(platform, device_types, 0, None, num_devices) != CL.CLERROR.SUCCESS or \
                    num_devices.value == 0:
                    continue

                device_ids = (CL.cl_device_id * num_devices.value)()
                if CL.clGetDeviceIDs(platform, device_types, num_devices.value, device_ids, None) != CL.CLERROR.SUCCESS:
                    continue

                for i in range(num_devices.value):
                    device_id = device_ids[i]
                    # Check OpenCL version.
                    if device_id is not None:
                        device_version_size = CL.c_size_t()
                        if CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_VERSION, 0, None, device_version_size) == CL.CLERROR.SUCCESS:
                            device_version = CL.create_string_buffer(device_version_size.value)
                            if CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_VERSION, device_version_size.value, device_version, None) == CL.CLERROR.SUCCESS:
                                device_version = str(device_version.value, 'ascii')

                                major, minor = device_version.split(' ')[1].split('.')
                                opencl_version = int(major)*10+int(minor)
                                if opencl_version >= 12:
                                    _opencl_device_ids.append(device_id)
            break
    return _opencl_device_ids

def get_available_devices_info() -> List[DeviceInfo]:
    """
    returns a list of available picklable DeviceInfo's
    """
    devices = []
    for device_index, device_id in enumerate(_get_opencl_device_ids()):
        device_name = 'undefined'
        device_total_memory = 0

        name_size = CL.c_size_t()
        if CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_NAME, 0, None, name_size) == CL.CLERROR.SUCCESS:
            name_value = CL.create_string_buffer(name_size.value)
            if CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_NAME, name_size.value, name_value, None) == CL.CLERROR.SUCCESS:
                device_name = str(name_value.value, 'ascii')

        global_mem_size = CL.cl_ulong()
        if CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_GLOBAL_MEM_SIZE, CL.sizeof(global_mem_size), CL.byref(global_mem_size), None) == CL.CLERROR.SUCCESS:
            device_total_memory = global_mem_size.value

        vendor_id = CL.cl_uint()
        CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_VENDOR_ID, CL.sizeof(vendor_id), CL.byref(vendor_id), None)
        vendor_id = vendor_id.value

        max_compute_units = CL.cl_uint()
        CL.clGetDeviceInfo(device_id, CL.CL_DEVICE_MAX_COMPUTE_UNITS, CL.sizeof(max_compute_units), CL.byref(max_compute_units), None)
        max_compute_units = max_compute_units.value

        performance_level = max_compute_units

        if vendor_id == 0x8086: # Intel device
            performance_level -= 1000

        devices.append( DeviceInfo(index=device_index, name=device_name, total_memory=device_total_memory, performance_level=performance_level ) )

    return devices

def get_default_device() -> Union[Device, None]:
    global _default_device
    if _default_device is None:
        _default_device = get_best_device()
    return _default_device

def set_default_device(device : Device):
    if not isinstance(device, Device):
        raise ValueError('device must be an instance of Device')

    global _default_device
    _default_device = device

def get_device(arg : Union[None, int, Device, DeviceInfo]) -> Union[Device, None]:
    """
    get physical TensorCL device.

        arg     None        - get default device
                int         - by index
                DeviceInfo  - by device info
                Device      - returns the same
    """
    global _devices

    if arg is None:
        return get_default_device()
    elif isinstance(arg, int):
        devices_info = get_available_devices_info()
        if arg < len(devices_info):
            arg = devices_info[arg]
        else:
            return None
    elif isinstance(arg, Device):
        return arg
    elif not isinstance(arg, DeviceInfo):
        raise ValueError(f'Unknown type of arg {arg.__class__}')

    device = _devices.get(arg, None)
    if device is None:
        device = _devices[arg] = Device(arg, _check=1)

    return device

def get_best_device() -> Union[Device, None]:
    """
    returns best device from available.
    """
    perf_level = -999999
    result = None
    for device_info in get_available_devices_info():
        dev_perf_level = device_info.get_performance_level()
        if perf_level < dev_perf_level:
            perf_level = dev_perf_level
            result = device_info
    if result is not None:
        result = get_device(result)
    return result

def cleanup_devices():
    global _devices

    for device in list(_devices.values()):
        device.cleanup()
    _devices = {}
