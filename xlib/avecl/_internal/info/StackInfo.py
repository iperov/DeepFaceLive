from ..AShape import AShape

class StackInfo:
    __slots__ = ['o_shape', 'axis']

    def __init__(self, shape, axis, stack_count):
        """
        Stack info

        arguments

            shape           AShape

            axis            Int

            stack_count     Int

        errors during the construction:

            ValueError

        result:

            .o_shape       AShape

            .axis     Int       positive axis argument
        """
        if axis < 0:
            axis = shape.ndim + 1 + axis
        if axis < 0 or axis > shape.ndim:
            raise ValueError(f'Wrong axis {axis}')

        if stack_count <= 0:
            raise ValueError(f'Invalid stack_count {stack_count}')

        self.o_shape = AShape( tuple(shape)[0:axis] + (stack_count,) + tuple(shape)[axis:] )
        self.axis = axis