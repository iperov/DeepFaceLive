from ..Tensor import Tensor

class Initializer:
    """
    Base class for tensor inititalizers
    """
    def initialize_tensor(self, tensor : Tensor):
        """
        Implement initialization of tensor

        You can compute the data using python and then call buffer.set(numpy_value)
        or call kernel.run( tensor.get_device(), tensor.get_buffer, ...) to initialize the data using OpenCL
        """
        raise NotImplementedError()

    def __str__(self): return 'Initializer'
    def __repr__(self): return self.__str__()
