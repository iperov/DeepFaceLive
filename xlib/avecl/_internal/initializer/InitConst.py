from ..backend import Kernel
from ..HKernel import HKernel
from ..SCacheton import SCacheton
from ..Tensor import Tensor
from .Initializer import Initializer


class InitConst(Initializer):

    def __init__(self, value=0):
        """
        arguments

         value(0)
        """
        super().__init__()
        self._value = value

    def initialize_tensor(self, tensor : Tensor):

        key = (InitConst, self._value, tensor.dtype)
        kernel = SCacheton.get_var(key)
        if kernel is None:
            kernel = Kernel(kernel_text=f"""
{HKernel.define_tensor('O', (tensor.shape.size,), tensor.dtype )}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME)
{{
    O_GLOBAL_STORE(get_global_id(0), (O_TYPE){self._value} );
}}
""")
            SCacheton.set_var(key, kernel)

        tensor.get_device().run_kernel( kernel, tensor.get_buffer(),
                                        global_shape=(tensor.shape.size,) )

    def __str__(self):  return f'InitConst low={self._low}, high={self._high}'

