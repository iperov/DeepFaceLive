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
        cleanup_devices()

__all__ = ['NCore']