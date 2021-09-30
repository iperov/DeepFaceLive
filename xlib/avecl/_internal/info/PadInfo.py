from typing import List

import numpy as np

from ..AShape import AShape


class PadInfo:
    """
    Pad info.

    arguments

        shape   AShape

        axes_paddings   list of (l_pad, r_pad)

                        if [0] == ... (Ellipsis), then left-side paddings will be filled with (0,0) for remain axes
                        if [-1] == ... , same for ride-side

    errors during the construction:

        ValueError

    result:

        .o_shape   AShape

    """

    __slots__ = ['o_shape','axes_paddings']

    def __init__(self, shape, axes_paddings : List):

        if Ellipsis in axes_paddings:
            if sum(1 if x == Ellipsis else 0 for x in axes_paddings) > 1:
                raise ValueError('only 1 ...(ellipsis) allowed in axes_paddings')
            if axes_paddings[0] == Ellipsis:
                axes_paddings = ((0,0),)*(shape.ndim-(len(axes_paddings)-1))+ axes_paddings[1:]
            elif axes_paddings[-1] == Ellipsis:
                axes_paddings = axes_paddings[:-1] + ((0,0),)*(shape.ndim-(len(axes_paddings)-1))
            else:
                raise ValueError('...(ellipsis) must be at the begin or the end of axes_paddings')

        if len(axes_paddings) != shape.ndim:
            raise ValueError(f'axes_paddings should match shape.ndim {shape.ndim}')


        self.axes_paddings = axes_paddings
        o_shape = []

        for axis, (axis_size, (l_pad, r_pad)) in enumerate(zip(shape, axes_paddings)):
            new_axis_size = l_pad + axis_size + r_pad
            o_shape.append(new_axis_size)

        self.o_shape = AShape(o_shape)
