from .SCacheton import SCacheton
from .Tensor import Tensor
from .backend import *

class NCore:
    """
    core functions
    """

    @staticmethod
    def cleanup():
        """
        try to cleanup all resources consumed by TensorCL.

        can raise Exception
        """
        SCacheton.cleanup()

        if Tensor._object_count != 0:
            raise Exception(f'Unable to cleanup while {Tensor._object_count} Tensor objects exist.')

        cleanup_devices()

__all__ = ['NCore']