import numpy as np

from ..backend import Kernel
from ..HKernel import HKernel
from ..SCacheton import SCacheton
from ..Tensor import Tensor
from .Initializer import Initializer


class InitRandomUniform(Initializer):

    def __init__(self, low=0, high=1):
        """
        arguments

         low(0)   low value

         high(1)  high value (exclusive)
        """
        super().__init__()
        self._low = low
        self._high = high

    def initialize_tensor(self, tensor : Tensor):

        key = (InitRandomUniform, self._low, self._high, tensor.dtype)
        kernel = SCacheton.get_var(key)
        if kernel is None:

            hl = self._high-self._low
            l = self._low

            if tensor.dtype in [np.bool_,np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32]:
                gen_expression = f'hash_uint_from_uint(gid+seed32) % {int(hl)} + {int(l)}'
            elif tensor.dtype in [np.int64]:
                gen_expression = f'hash_ulong_from_ulong(gid+seed64) % {int(hl)} + {int(l)}'
            elif tensor.dtype in [np.uint64]:
                gen_expression = f'hash_ulong_from_ulong(gid+seed64) % {int(hl)} + {int(l)}'
            elif tensor.dtype in [np.float16, np.float32]:
                gen_expression = f'hash_float_from_uint(gid+seed32)*{hl} + {l}'

            kernel = Kernel(kernel_text=f"""
{HKernel.include_hash()}
{HKernel.define_tensor('O', (tensor.shape.size,), tensor.dtype )}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, uint seed32, ulong seed64)
{{
    size_t gid = get_global_id(0);
    O_GLOBAL_STORE(gid, {gen_expression} );
}}
""")
            SCacheton.set_var(key, kernel)


        tensor.get_device().run_kernel( kernel, tensor.get_buffer(),
                                        np.uint32(np.random.randint(np.iinfo(np.uint32).max, dtype=np.uint32)),
                                        np.uint64(np.random.randint(np.iinfo(np.uint64).max, dtype=np.uint64)),
                                        global_shape=(tensor.shape.size,) )

    def __str__(self):  return f'InitRandomUniform low={self._low}, high={self._high}'

