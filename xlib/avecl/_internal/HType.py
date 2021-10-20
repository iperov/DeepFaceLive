import operator
from typing import Iterable, List
import numpy as np

scalar_types = [int, float, np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64,
                np.float16, np.float32, np.bool_]

np_scalar_types = [np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64, np.int64,
                    np.float16, np.float32, np.bool_]

_np_dtype_to_cl = {
    np.bool_   : 'bool',
    np.uint8   : 'uchar',
    np.int8    : 'char',
    np.uint16  : 'ushort',
    np.int16   : 'short',
    np.uint32  : 'uint',
    np.int32   : 'int',
    np.uint64  : 'ulong',
    np.int64   : 'long',
    np.float16 : 'half',
    np.float32 : 'float',
}

_np_dtype_weight = {
    np.bool_   : 1,
    np.uint8   : 2,
    np.int8    : 3,
    np.uint16  : 4,
    np.int16   : 5,
    np.uint32  : 6,
    np.int32   : 7,
    np.uint64  : 8,
    np.int64   : 9,
    np.float16 : 10,
    np.float32 : 11
}

class HType:
    """
    Helper functions for types.
    """

    def is_scalar_type(value):
        return value.__class__ in scalar_types

    def get_np_scalar_types() -> List:
        return np_scalar_types

    def is_obj_of_np_scalar_type(obj) -> bool:
        return obj.__class__ in np_scalar_types

    def np_dtype_to_cl(dtype : np.dtype) -> str:
        return _np_dtype_to_cl[ np.dtype(dtype).type ]

    def get_most_weighted_dtype( dtype_list ):
        dtype_list = [ np.dtype(dtype) for dtype in dtype_list ]

        dtype_list = [ (_np_dtype_weight[dtype.type], dtype) for dtype in dtype_list ]
        dtype_list = sorted(dtype_list, key=operator.itemgetter(0), reverse=True)
        return dtype_list[0][1]

    def hashable_slices(slices):
        """
        Convert list of slice to hashable arg.
        """
        if not isinstance(slices, Iterable):
            slices = (slices,)
        normalized_slices = []
        for x in slices:
            if isinstance(x, slice):
                normalized_slices.append( (x.start, x.stop, x.step) )
            elif x is Ellipsis or x is None:
                normalized_slices.append(x)
            else:
                normalized_slices.append(int(x))
        return tuple(normalized_slices)


__all__ = ['HType']