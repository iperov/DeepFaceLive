from typing import List

import numpy as np

from .backend import Device
from .HTensor import HTensor
from .HType import HType
from .Tensor import Tensor
from .AShape import AShape

class HArgs:
    """
    Helper functions for list of arguments
    """

    @staticmethod
    def decompose(args):
        """
        decompose list of args of Tensor and supported numeric values

         returns ( shape_list,   #  if scalar value -> shape is None
                   dtype_list,   #
                   kernel_args_list   #
                 )
        """
        shape_list = []
        dtype_list = []
        kernel_args_list = []
        for arg in args:

            if isinstance(arg, Tensor):
                shape_list.append(arg.shape)
                dtype_list.append(arg.dtype)
                kernel_args_list.append(arg.get_buffer())
            else:

                if isinstance(arg, int):
                    dtype, arg = np.int32, np.int32(arg)
                elif isinstance(arg, float):
                    dtype, arg = np.float32, np.float32(arg)
                elif HType.is_obj_of_np_scalar_type(arg):
                    dtype = arg.__class__
                else:
                    raise ValueError(f'Unsupported type of arg: {arg.__class__} Use Tensor or number type.')

                shape_list.append(None)
                dtype_list.append(dtype)
                kernel_args_list.append(arg)

        return tuple(shape_list), tuple(dtype_list), tuple(kernel_args_list)

    @staticmethod
    def get_shapes(args : List[Tensor]) -> List[AShape]:
        """
        """
        return tuple(t.shape for t in args)

    @staticmethod
    def check_zero_get_length(args) -> int:
        """
        raises an error if len(args) == 0, otherwise returns len
        """
        args_len = len(args)
        if len(args) == 0:
            raise ValueError('args must be specified')
        return args_len

    @staticmethod
    def check_get_same_device(args : List[Tensor]) -> Device:
        """
        check all device of tensors are the same and return the device
        """
        result = HTensor.all_same_device(args)
        if not result:
            raise ValueError('all Tensors must have the same device')
        return args[0].get_device()

    @staticmethod
    def check_all_tensors(args : List[Tensor]):
        """
        """
        if not all (isinstance(tensor, Tensor) for tensor in args):
            raise ValueError('All values must have type of Tensor')

    @staticmethod
    def check_get_same_shape(args : List[Tensor]) -> AShape:
        """
        check all shapes of tensors are the same and return the shape
        """
        shape = args[0].shape
        if not all (t.shape == shape for t in args):
            raise ValueError('All tensors must have the same shape')
        return shape


    @staticmethod
    def filter_tensor(args, raise_on_empty : bool):
        """
        get only tensors from the list
        """
        tensor_args = [arg for arg in args if isinstance(arg, Tensor) ]
        if raise_on_empty and len(tensor_args) == 0:
            raise ValueError('At least one arg must be a Tensor')
        return tensor_args

__all__ = ['HArgs']
