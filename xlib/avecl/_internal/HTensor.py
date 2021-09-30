from typing import List, Union

from .Tensor import *


class HTensor:
    """
    Helper functions for Tensor
    """

    @staticmethod
    def all_same_device( tensor_or_list : Union[Tensor, List[Tensor] ] ) -> bool:
        """
        check if all tensors in a list use the same device
        """
        if not isinstance(tensor_or_list, (list,tuple)):
            tensor_or_list = (tensor_or_list,)

        device = tensor_or_list[0].get_device()
        return all( device == tensor.get_device() for tensor in tensor_or_list )

__all__ = ['HTensor']
