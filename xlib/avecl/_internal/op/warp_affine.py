import numpy as np

from ..AShape import AShape
from ..initializer import InitCoords2DArange
from ..SCacheton import SCacheton
from ..Tensor import Tensor
from .matmul import matmul
from .remap import remap

def warp_affine (input_t : Tensor, affine_t : Tensor, output_size=None, dtype=None) -> Tensor:
    """
    arguments

        input_t     Tensor(...,H,W)

        affine_t    Tensor(...,2,3)
                    affine matrix

                    example of identity affine matrix
                    [1,0,0],
                    [0,1,0]

        ...-head part of shapes will be broadcasted to each other

        output_size(None)

                    tuple of 2 ints (HW)
                    of output size
                    if None , size will not be changed

    """
    op = SCacheton.get(_WarpAffineOp, input_t.shape, input_t.dtype,  affine_t.shape, affine_t.dtype, output_size)

    affine_t = affine_t.transpose( op.affine_transpose_axes, dtype=np.float32 ).reshape( (-1,3,2) )

    coords_t = Tensor(op.coords_shape, np.float32, device=input_t.get_device(), initializer=op.coords_init )
    coords_t = coords_t.reshape(op.coords_reshape)
    coords_t = matmul(coords_t, affine_t).reshape(op.coords_affined_shape)

    output_t = remap(input_t, coords_t, dtype=dtype)
    return output_t


class _WarpAffineOp():
    def __init__(self, i_shape : AShape, i_dtype, a_shape : AShape, a_dtype, o_size):
        if np.dtype(i_dtype).type == np.bool_:
            raise ValueError('np.bool_ dtype of i_dtype is not supported.')
        if np.dtype(a_dtype).type == np.bool_:
            raise ValueError('np.bool_ dtype of a_dtype is not supported.')
        if i_shape.ndim < 2:
            raise ValueError('i_shape.ndim must be >= 2 (...,H,W)')
        if a_shape.ndim < 2:
            raise ValueError(f'a_shape.ndim must be >= 2 (...,2,3)')
        if a_shape[-2] != 2 or a_shape[-1] != 3:
            raise ValueError('Last a_shape dims must be == (...,2,3)')

        IH,IW = i_shape[-2:]
        if o_size is not None:
            OH,OW = o_size
        else:
            OH,OW = IH,IW

        self.coords_shape = AShape( (OH,OW,3) )
        self.coords_affined_shape = AShape( (OH,OW,2) )

        if a_shape.ndim > 2:
            self.coords_shape = a_shape[:-2] + self.coords_shape
            self.coords_affined_shape = a_shape[:-2] + self.coords_affined_shape

        self.coords_init = InitCoords2DArange(0,OH-1,0,OW-1)
        self.coords_reshape = (-1,OH*OW,3)
        self.affine_transpose_axes = a_shape.axes_arange().swapped_axes(-2,-1)
