import weakref
from typing import Iterable, Union

import numpy as np

from .AShape import *
from .backend import *
from .HType import *


class Tensor:
    ### CONSTRUCTORS

    def __init__(self, shape : Union[AShape, Iterable],
                       dtype : np.dtype,
                       device : Union[None, int, Device, DeviceInfo] = None,
                       initializer : 'Initializer' = None,
                       ):
        Tensor._object_count += 1

        self._shape = shape = AShape(shape)
        self._dtype = dtype = np.dtype(dtype)
        self._device = device = get_device(device)
        if device is None:
            raise Exception('No device.')

        self._seq_id = Tensor._seq_id = Tensor._seq_id + 1
        self._buffer = Buffer(device, size=shape.size*dtype.itemsize,
                              on_initialize= lambda initializer=initializer, wself=weakref.ref(self): initializer.initialize_tensor( wself() ) if initializer is not None else None )

    @staticmethod
    def from_value(value, dtype=None, device:Union[None,int,Device,DeviceInfo]=None) -> 'Tensor':
        if isinstance(value, Tensor):
            device = value.get_device()
        elif not isinstance(value, np.ndarray):
            if HType.is_scalar_type(value):
                if dtype is None:
                    raise ValueError('dtype must be specified for single value')
                value = np.array([value], dtype=dtype)
            elif isinstance(value, Iterable):
                if dtype is None:
                    raise ValueError('dtype must be specified for Iterable of values')
                value = np.array(value, dtype=dtype)
            else:
                raise ValueError(f'Unsupported value type {value.__class__}')

        return Tensor(shape=value.shape, dtype=value.dtype, device=device).set(value)

    ### PROPERTIES

    @property
    def shape(self): return self._shape
    @property
    def ndim(self): return len(self._shape)
    @property
    def dtype(self) -> np.dtype: return self._dtype
    @property
    def name(self) -> str: return f'#{self.get_seq_id()}'

    ### GETTERS/SETTERS

    def get_buffer(self) -> Buffer: return self._buffer
    def get_device(self) -> Device: return self._device
    def get_seq_id(self) -> int: return self._seq_id

    def set(self, value : Union['Tensor',np.ndarray,int,float]) -> 'Tensor':
        if isinstance(value, Tensor):
            if self.shape.size != value.shape.size:
                raise ValueError('Unable to set the data from other tensor: shape.size is not the same.')
            self.get_buffer().set(value.get_buffer())
        else:
            if isinstance(value, np.ndarray):
                value = value.astype(self.dtype)
            else:
                if HType.is_scalar_type(value):
                    value = np.array([value], dtype=self.dtype)
                elif isinstance(value, Iterable):
                    value = np.array(value, dtype=self.dtype)
                else:
                    raise ValueError(f'Unsupported value type {value.__class__}')

            self.get_buffer().set(value)
        return self

    def np(self, out=None):
        """Returns numpy value of a Tensor"""
        return self.get_buffer().np(self.shape, self.dtype, out=out)


    ### OPERATORS

    def __add__(self, value) -> 'Tensor': ...
    def __radd__(self, value) -> 'Tensor': ...
    def __sub__(self, value) -> 'Tensor': ...
    def __rsub__(self, value) -> 'Tensor': ...
    def __mul__(self, value) -> 'Tensor': ...
    def __rmul__(self, value) -> 'Tensor': ...
    def __truediv__(self, value) -> 'Tensor': ...
    def __rtruediv__(self, value) -> 'Tensor': ...
    def __neg__(self) -> 'Tensor': ...
    def __getitem__(self, slices) -> 'Tensor': ...
    def __setitem__(self, slices, value): ...

    def as_shape(self, shape) -> 'Tensor': ...
    def cast(self, dtype) -> 'Tensor': ...
    def copy(self) -> 'Tensor': ...
    def max(self, axes=None, keepdims=False) -> 'Tensor': ...
    def mean(self, axes=None, keepdims=False) -> 'Tensor': ...
    def min(self, axes=None, keepdims=False) -> 'Tensor': ...
    def reshape(self, new_shape) -> 'Tensor': ...
    def sum(self, axes=None, keepdims=False) -> 'Tensor': ...
    def std(self, axes=None, keepdims=False) -> 'Tensor': ...
    def transpose(self, axes_order, op_text=None, dtype=None) -> 'Tensor': ...

    @property
    def T(self): return self.transpose( tuple(range(self.shape.ndim-1,-1,-1)) )

    ### INTERNAL METHODS

    def __del__(self):
        Tensor._object_count -= 1

    _object_count = 0
    _seq_id = 0

__all__ = ['Tensor']
