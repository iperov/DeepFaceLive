from ..AShape import AShape
from ..AAxes import AAxes

class TransposeInfo:
    """
    TransposeInfo

    arguments

        shape           AShape

        axes_order      AAxes

    errors during the construction:

        ValueError

    result

        .o_shape   AShape

        .no_changes     bool       transpose changes nothing

    """

    __slots__ = ['no_changes', 'o_shape']

    def __init__(self, shape : AShape, axes_order : AAxes):
        if shape.ndim != axes_order.ndim:
            raise ValueError('axes must match the shape')

        # Axes order changes nothing?
        self.o_shape = shape[axes_order]
        self.no_changes = axes_order == shape.axes_arange()



