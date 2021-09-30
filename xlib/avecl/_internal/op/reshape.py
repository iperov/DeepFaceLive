from typing import Iterable

from ..Tensor import Tensor
from ..SCacheton import SCacheton
from ..info import ReshapeInfo


def reshape(input_t : Tensor, new_shape : Iterable, copy=True) -> Tensor:
    """
    reshape operator

    arguments

        new_shape    Iterable of ints

        copy(True)      if True, produces new Tensor
                        otherwise result tensor points to the same memory

    Produces reference Tensor with new shape.
    """
    info = SCacheton.get(ReshapeInfo, input_t.shape, tuple(int(x) for x in new_shape) )

    if copy:
        return Tensor(info.o_shape, input_t.dtype, device=input_t.get_device()).set(input_t)
    return input_t.as_shape( info.o_shape )

