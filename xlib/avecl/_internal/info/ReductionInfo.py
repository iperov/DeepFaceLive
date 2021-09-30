from ..AShape import AShape

class ReductionInfo:
    """
    Reduction info

    arguments

        shape       AShape

        axes        AAxes

        keepdims    bool

    can raise ValueError, TypeError during the construction
    """

    __slots__ = [
        'reduction_axes',   # sorted reduction AAxes
        'o_axes',           # remain AAxes after reduction
        'o_shape',          # result AShape of reduction
        'o_shape_kd',       # result AShape of reduction with keepdims
    ]

    def __init__(self, shape, axes, keepdims):
        shape_axes = shape.axes_arange()

        if axes.is_none_axes():
            axes = shape_axes

        # Check correctness of axes
        for axis in axes:
            if axis not in shape_axes:
                raise ValueError(f'Wrong axis {axis} not in {shape_axes}')

        self.reduction_axes = reduction_axes = axes.sorted()

        # Output axes. Remove axes from shape_axes
        self.o_axes = o_axes = shape_axes - axes

        if o_axes.is_none_axes():
            o_shape = AShape( (1,) )
        else:
            o_shape = shape[o_axes]

        self.o_shape = o_shape
        self.o_shape_kd = AShape( 1 if axis in reduction_axes else shape[axis] for axis in range(shape.ndim))

        if keepdims:
            self.o_shape = self.o_shape_kd