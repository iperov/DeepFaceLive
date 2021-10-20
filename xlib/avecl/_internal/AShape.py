from collections import Iterable
from typing import Tuple, List

from .AAxes import AAxes


class AShape(Iterable):
    __slots__ = ['shape','size','ndim']

    def __init__(self, shape):
        """
        Constructs valid shape from user argument

        arguments

            shape       AShape
                        Iterable

        AShape cannot be scalar shape, thus minimal AShape is (1,)

        can raise ValueError during the construction
        """

        if isinstance(shape, AShape):
            self.shape = shape.shape
            self.size = shape.size
            self.ndim = shape.ndim
        else:
            if isinstance(shape, (int,float) ):
                shape = (int(shape),)

            if isinstance(shape, Iterable):
                size = 1
                valid_shape = []
                for x in shape:
                    if x is None:
                        raise ValueError(f'Incorrent value {x} in shape {shape}')
                    x = int(x)
                    if x < 1:
                        raise ValueError(f'Incorrent value {x} in shape {shape}')
                    valid_shape.append(x)
                    size *= x # Faster than np.prod()

                self.shape = tuple(valid_shape)
                self.ndim = len(self.shape)
                if self.ndim == 0:
                    # Force (1,) shape for scalar shape
                    self.ndim = 1
                    self.shape = (1,)
                self.size = size
            else:
                raise ValueError('Invalid type to create AShape')

    def copy(self) -> 'AShape':
        return AShape(self)

    def as_list(self) -> List[int]:
        return list(self.shape)

    def check_axis(self, axis : int) -> int:
        """
        Check axis and returns normalized axis value

        can raise ValueError
        """
        if axis < 0:
            axis += self.ndim

        if axis < 0 or axis >= self.ndim:
            raise ValueError(f'axis {axis} out of bound of ndim {self.ndim}')
        return axis

    def axes_arange(self) -> AAxes:
        """
        Returns tuple of axes arange.

         Example (0,1,2) for ndim 3
        """
        return AAxes(range(self.ndim))

    def replaced_axes(self, axes, dims) -> 'AShape':
        """
        returns new AShape where axes replaced with new dims
        """
        new_shape = list(self.shape)
        ndim = self.ndim
        for axis, dim in zip(axes, dims):
            if axis < 0:
                axis = ndim + axis
            if axis < 0 or axis >= ndim:
                raise ValueError(f'invalid axis value {axis}')

            new_shape[axis] = dim
        return AShape(new_shape)


    def split(self, axis) -> Tuple['AShape', 'AShape']:
        """
        split AShape at specified axis

        returns two AShape before+exclusive and inclusive+after
        """
        if axis < 0:
            axis = self.ndim + axis
        if axis < 0 or axis >= self.ndim:
            raise ValueError(f'invalid axis value {axis}')

        return self[:axis], self[axis:]

    def transpose_by_axes(self, axes) -> 'AShape':
        """
        Same as AShape[axes]

        Returns AShape transposed by axes.

         axes       AAxes
                    Iterable(list,tuple,set,generator)
        """
        return AShape(self.shape[axis] for axis in AAxes(axes) )

    def __hash__(self): return self.shape.__hash__()
    def __eq__(self, other):
        if isinstance(other, AShape):
            return self.shape == other.shape
        elif isinstance(other, Iterable):
            return self.shape == tuple(other)
        return False
    def __iter__(self): return self.shape.__iter__()
    def __len__(self): return len(self.shape)
    def __getitem__(self,key):
        if isinstance(key, Iterable):
            if isinstance(key, AAxes):
                if key.is_none_axes():
                    return self
            return self.transpose_by_axes(key)
        elif isinstance(key, slice):
            return AShape(self.shape[key])

        return self.shape[key]

    def __radd__(self, o):
        if isinstance(o, Iterable):
            return AShape( tuple(o) + self.shape)
        else:
            raise ValueError(f'unable to use type {o.__class__} in AShape append')
    def __add__(self, o):
        if isinstance(o, Iterable):
            return AShape( self.shape + tuple(o) )
        else:
            raise ValueError(f'unable to use type {o.__class__} in AShape append')


    def __str__(self):  return str(self.shape)
    def __repr__(self): return 'AShape' + self.__str__()

__all__ = ['AShape']
