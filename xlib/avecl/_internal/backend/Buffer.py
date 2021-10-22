from typing import Iterable, Union

import numpy as np

from . import OpenCL as CL

class Buffer:
    __slots__ = ['_device','_cl_mem','_size','_on_initialize']

    def __init__(self, device : 'Device', size : int, on_initialize = None):
        """
        represents physical buffer associated with physical device

         device     Device

         size       int
        """

        Buffer._object_count += 1
        self._device = device
        self._size = size
        self._cl_mem = None
        self._on_initialize = on_initialize

    def __del__(self):
        #print('Buffer.__del__')
        Buffer._object_count -= 1
        self.free_cl_mem()

    def get_device(self) -> 'Device': return self._device
    def get_size(self) -> int: return self._size

    def has_cl_mem(self) -> bool: return self._cl_mem is not None
    def get_cl_mem(self) -> CL.cl_mem:
        if self._cl_mem is None:
            self._cl_mem = self._device._cl_mem_pool_alloc(self._size)
            if self._on_initialize is not None:
                self._on_initialize()

        return self._cl_mem

    def free_cl_mem(self):
        if self._cl_mem is not None:
            self._device._cl_mem_pool_free(self._cl_mem)
            self._cl_mem = None

    def set(self, value : Union['Buffer', np.ndarray]):
        """
        Parameters

            value   Buffer    copy data from other Buffer.

                    np.ndarray  copies values from ndarray
                                to Buffer's memory

        """
        if isinstance(value, Buffer):
            if self != value:
                if self._size != value._size:
                    raise Exception(f'Unable to copy from Buffer with {value._size} size to buffer with {self._size} size.')

                if self._device == value._device:
                    CL.clEnqueueCopyBuffer(self._device._get_ctx_q(), value.get_cl_mem(), self.get_cl_mem(), 0, 0, self._size, 0, None, None)
                else:
                    # Transfer between devices will cause low performance
                    raise NotImplementedError()
        else:
            if not isinstance(value, np.ndarray):
                raise ValueError (f'Invalid type {value.__class__}. Must be np.ndarray.')

            if value.nbytes != self._size:
                raise ValueError(f'Value size {value.nbytes} does not match Buffer size {self._size}.')

            if not value.flags.contiguous:
                value = value.reshape(-1)
            if not value.flags.contiguous:
                raise ValueError ("Unable to write from non-contiguous np array.")

            ev = CL.cl_event()

            clr = CL.clEnqueueWriteBuffer(self._device._get_ctx_q(), self.get_cl_mem(), False, 0, value.nbytes, value.ctypes.data_as(CL.c_void_p), 0, None, ev)
            if clr != CL.CLERROR.SUCCESS:
                raise Exception(f'clEnqueueWriteBuffer error: {clr}')

            CL.clWaitForEvents(1, ( CL.cl_event * 1 )(ev) )
            CL.clReleaseEvent(ev)

    def np(self, shape : Iterable, dtype : np.dtype, out=None):
        """
        Returns data of buffer as np.ndarray with specified shape and dtype
        """
        if out is None:
            out = np.empty (shape, dtype)

        if out.nbytes != self._size:
            raise ValueError(f'Unable to represent Buffer with size {self._size} as shape {shape} with dtype {dtype}')

        clr = CL.clEnqueueReadBuffer(self._device._get_ctx_q(), self.get_cl_mem(), True, 0, self._size, out.ctypes.data, 0, None, None)
        if clr != CL.CLERROR.SUCCESS:
            raise Exception(f'clEnqueueReadBuffer error: {clr}')

        return out

    def __str__(self):
        return f'Buffer [{self._size} bytes][{f"{self._cl_mem.value}" if self._cl_mem is not None else "unallocated"}] on {str(self._device)}'

    def __repr__(self):
        return self.__str__()

    _object_count = 0
