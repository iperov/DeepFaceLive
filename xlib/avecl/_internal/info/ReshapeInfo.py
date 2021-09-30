from ..AShape import AShape

class ReshapeInfo:
    """
    Reshape info.
    can raise ValueError,TypeError during the construction

    arguments

        shape           AShape

        target_shape    Iterable of ints
                        can be any len and contains only one '-1'
    Example

     shape        (2, 512, 8, 8, 64)
     target_shape (2, 512, -1)
     o_shape      (2, 512, 4096)
    """

    __slots__ = ['o_shape']

    def __init__(self, shape, target_shape):
        o_shape = []

        remain_size = shape.size

        unk_axis = None
        for t_size in target_shape:
            t_size = int(t_size)
            if t_size != -1:
                mod = remain_size % t_size
                if mod != 0:
                    raise ValueError(f'Cannot reshape {shape} to {target_shape}.')
                remain_size /= t_size
            else:
                if unk_axis is not None:
                    raise ValueError('Can specify only one unknown dimension.')
                unk_axis = len(o_shape)
            o_shape.append( t_size )

        if unk_axis is not None:
            o_shape[unk_axis] = int(remain_size)
        self.o_shape = AShape(o_shape)