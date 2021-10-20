from .op import *
from .AShape import *
from .backend import *
from .Tensor import Tensor

def Tensor__str__(self : Tensor): return f"T {self.name} {self.shape} {self.dtype.name}"
Tensor.__str__ = Tensor__str__

def Tensor__repr__(self : Tensor):
    s  = self.__str__() + '\n'
    s += str(self.np()) + '\n'
    s += self.__str__()
    return s
Tensor.__repr__ = Tensor__repr__

def Tensor__add__(self : Tensor, value) -> Tensor:
    return add(self, value)
Tensor.__add__ = Tensor__add__

def Tensor__radd__(self : Tensor, value) -> Tensor:
    return add(value, self)
Tensor.__radd__ = Tensor__radd__

def Tensor__sub__(self : Tensor, value) -> Tensor:
    return sub(self, value)
Tensor.__sub__ = Tensor__sub__

def Tensor__rsub__(self : Tensor, value) -> Tensor:
    return sub(value, self)
Tensor.__rsub__ = Tensor__rsub__

def Tensor__mul__(self : Tensor, value) -> Tensor:
    if self == value:
        return square(self)
    return mul(self, value)
Tensor.__mul__ = Tensor__mul__

def Tensor__rmul__(self : Tensor, value) -> Tensor:
    if self == value:
        return square(self)
    return mul(value, self)
Tensor.__rmul__ = Tensor__rmul__

def Tensor__truediv__(self : Tensor, value) -> Tensor:
    return div(self, value)
Tensor.__truediv__ = Tensor__truediv__

def Tensor__rtruediv__(self : Tensor, value) -> Tensor:
    return div(value, self)
Tensor.__rtruediv__ = Tensor__rtruediv__

def Tensor___neg__(self : Tensor):
    raise NotImplementedError()
Tensor.___neg__ = Tensor___neg__

Tensor.__getitem__ = slice_
Tensor.__setitem__ = slice_set

def Tensor_as_shape(self : Tensor, shape) -> Tensor:
    return TensorRef(self, shape)
Tensor.as_shape = Tensor_as_shape

Tensor.cast = cast
def Tensor_copy(self : Tensor) -> Tensor:
    return Tensor.from_value(self)
Tensor.copy = Tensor_copy

Tensor.max = reduce_max
Tensor.mean = reduce_mean
Tensor.min = reduce_min
Tensor.reshape = reshape
Tensor.sum = reduce_sum
Tensor.std = reduce_std
Tensor.transpose = transpose

class TensorRef(Tensor):
    """
    TensorRef used to interpret existing Tensor with different shape.
    use Tensor.as_ref() method
    """

    def __init__(self, t : Tensor, shape):
        shape = AShape(shape)
        if t.shape.size != shape.size:
            raise ValueError(f'Cannot interpet shape {t.shape} as ref shape {shape}')
        super().__init__(shape, t.dtype, device=t.get_device())
        self._t = t

    # Forward methods to original tensor
    def get_seq_id(self) -> int:              return self._t.get_seq_id()
    def get_buffer(self) -> Buffer: return self._t.get_buffer()
    def get_device(self) -> Device: return self._t.get_device()

__all__ = []
