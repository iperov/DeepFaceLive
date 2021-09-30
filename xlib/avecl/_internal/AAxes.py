from collections import Iterable

class AAxes(Iterable):
    __slots__ = ['axes','ndim','_inversed']

    def __init__(self, axes, shape_ndim=None):
        """
        Constructs AAxes from user argument

        arguments

        axes        AAxes
                    Int
                    Iterable of ints
                    None

        shape_ndim(None)    provide shape_ndim if axes contain negative values

        can raise an errors during the construction

        AAxes supports:

        A+B : concat A_axes with B_axes

        A-B : removes B_axes from A_axes
        """

        if isinstance(axes, AAxes):
            self.axes = axes.axes
            self.ndim = axes.ndim
            self._inversed = axes._inversed
        elif axes is None:
            self.axes = None
            self.ndim = None
            self._inversed = None
        else:
            if not isinstance(axes, Iterable):
                axes = (axes,)

            if isinstance(axes, Iterable):
                valid_axes = []
                for x in axes:
                    if x is None:
                        raise ValueError(f'Incorrent value {x} in axes {axes}')
                    x = int(x)
                    if x < 0:
                        if shape_ndim is None:
                            raise ValueError(f'Incorrent value {x} in axes {axes}, or provide shape_ndim')
                        x = shape_ndim + x

                    if x in valid_axes:
                        raise ValueError(f'Axes must contain unique values.')
                    valid_axes.append(x)

                self.axes = tuple(valid_axes)
                self.ndim = len(self.axes)
                self._inversed = None

    def is_none_axes(self):
        """
        returns True if AAxes is constructed with (None) argument, i.e. all-axes
        """
        return self.axes is None

    def sorted(self) -> 'AAxes':
        """
        returns sorted AAxes
        """
        return AAxes(sorted(self.axes))

    def swapped_axes(self, axis_a, axis_b) -> 'AAxes':
        x = list(self.axes)
        if axis_a < 0:
            axis_a = len(x) + axis_a
        if axis_b < 0:
            axis_b = len(x) + axis_b

        x[axis_b], x[axis_a] = x[axis_a], x[axis_b]

        return AAxes( tuple(x) )

    def inversed(self) -> 'AAxes':
        """
        Returns inversed axes order

        Example:

         for (0,2,3,1)  returns (0,3,1,2)
        """
        if self.is_none_axes():
            raise Exception(f'none-axes does not support inversed(). Handle none-axes by calling .is_none_axes()')

        if self._inversed is None:
            x = { axis:i for i,axis in enumerate(self.axes) }
            t = []
            for i in range(self.ndim):
                axis = x.get(i, None)
                if axis is None:
                    raise Exception(f'axes {self.axes} are inconsistent to do inverse order.')
                t.append(axis)
            self._inversed = AAxes(t)

        return self._inversed


    def __hash__(self): return self.axes.__hash__()
    def __eq__(self, other):
        if isinstance(other, AAxes):
            return self.axes == other.axes
        elif isinstance(other, Iterable):
            return self.axes == tuple(other)
        return False
    def __iter__(self):
        if self.is_none_axes():
            raise Exception(f'none-axes does not support iteration. Handle none-axes by calling .is_none_axes()')
        return self.axes.__iter__()

    def __len__(self): return self.ndim
    def __getitem__(self,key):
        if self.is_none_axes():
            raise Exception(f'none-axes does not support indexing. Handle none-axes by calling .is_none_axes()')

        elif isinstance(key, slice):
            return AAxes(self.axes[key])

        return self.axes[key]

    def __radd__(self, o):
        if isinstance(o, Iterable):
            return AAxes( tuple(o) + self.axes)
        else:
            raise ValueError(f'unable to use type {o.__class__} in AAxes append')
    def __add__(self, o):
        if isinstance(o, Iterable):
            return AAxes( self.axes + tuple(o) )
        else:
            raise ValueError(f'unable to use type {o.__class__} in AAxes append')

    def __rsub__(self, o):
        if isinstance(o, Iterable):
            new_axes = []
            for axis in o:
                if axis not in self.axes:
                    new_axes.append(axis)

            return AAxes(new_axes)
        else:
            raise ValueError(f'unable to use type {o.__class__} in AAxes substraction')

    def __sub__(self, o):
        if isinstance(o, Iterable):
            new_axes = []
            o_axes = tuple(o)
            for axis in self.axes:
                if axis not in o_axes:
                    new_axes.append(axis)

            return AAxes(new_axes)
        else:
            raise ValueError(f'unable to use type {o.__class__} in AAxes substraction')

    def __str__(self):
        if self.is_none_axes():
            return '(None)'
        return str(self.axes)

    def __repr__(self): return 'AAxes' + self.__str__()

__all__ = ['AAxes']