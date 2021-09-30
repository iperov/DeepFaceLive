import numpy as np

from ..backend import Kernel
from ..HKernel import HKernel
from ..SCacheton import SCacheton
from ..Tensor import Tensor
from .Initializer import Initializer

class InitCoords2DArange(Initializer):

    def __init__(self, h_start, h_stop, w_start, w_stop):
        """
        Initialize (...,H,W,D) tensor with coords arange
        D == 2(x,y) or 3 (x,y,1)

        arguments

            h_start     float     height start value (inclusive)

            h_stop      float     height stop value (inclusive)

            w_start     float     width start value (inclusive)

            w_stop      float     width stop value (inclusive)

        """
        super().__init__()
        self._h_start = h_start
        self._h_stop = h_stop
        self._w_start = w_start
        self._w_stop = w_stop

    def initialize_tensor(self, tensor : Tensor):
        shape = tensor.shape
        dtype = tensor.dtype

        if shape.ndim < 3:
            raise ValueError(f'tensor.shape.ndim must be >= 3 (...,H,W,D)')

        OH,OW,OD = shape[-3:]
        if OD not in [2,3]:
            raise ValueError(f'last dim D {OD} must == 2 or 3')

        if OH > 1:
            h_step = (self._h_stop-self._h_start) / (OH-1)
        else:
            h_step = 0

        if OW > 1:
            w_step = (self._w_stop-self._w_start) / (OW-1)
        else:
            w_step = 0

        key = (InitCoords2DArange, dtype)
        kernel = SCacheton.get_var(key)
        if kernel is None:
            kernel = Kernel(kernel_text=f"""

{HKernel.define_tensor_type('O', tensor.dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME  , float h_start, float h_step
                                                    , float w_start, float w_step,
                                                    uint O0, uint O1, uint O2)
{{
    size_t gid = get_global_id(0);

    {HKernel.decompose_idx_to_axes_idxs('gid', 'O', 3)}

    O_TYPE v;
    if (o2 == 0)
        v = w_start+o1*w_step;
    else
    if (o2 == 1)
        v = h_start+o0*h_step;
    else
        v = 1;

    O_GLOBAL_STORE(gid, v);
}}
""")
            SCacheton.set_var(key, kernel)

        tensor.get_device().run_kernel( kernel, tensor.get_buffer(),
                             np.float32(self._h_start), np.float32(h_step),
                             np.float32(self._w_start), np.float32(w_step),
                             np.uint32(OH), np.uint32(OW), np.uint32(OD),
                             global_shape=(shape.size,) )

    def __str__(self):  return f'CoordsArange'
