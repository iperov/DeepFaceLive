from collections import Iterable
import math

class Conv2DInfo:
    """
    Conv2DInfo

    arguments

     H, W        int            axes sizes
     KH, KW      int            kernel sizes
     stride      int
     dilation    int

     padding     'valid'        no padding
                 'same'         output size will be the same
                                or divided by stride
                 int            padding value for all sides

                 Iterable of 4 ints
                                paddings for left,top,right,bottom sides

    errors during the construction:

        ValueError

    result:

        .PADL .PADR  paddings for W axis
        .PADT .PADB  paddings for H axis

        .OH .OW      result axes

        .OH_T .OW_T  result transposed axes.
                    it is None if padding != 'valid','same'
    """

    __slots__ = ['PADL', 'PADR', 'PADT', 'PADB', 'OH', 'OW', 'OH_T', 'OW_T']

    def __init__(self, H, W, KH, KW, stride, dilation, padding):
        # Effective kernel sizes with dilation
        EKH = (KH-1)*dilation + 1
        EKW = (KW-1)*dilation + 1

        # Determine pad size of sides
        OH_T = OW_T = None
        if padding == 'valid':
            PADL = PADT = PADR = PADB = 0
            OH_T =  H * stride + max(EKH - stride, 0)
            OW_T =  W * stride + max(EKW - stride, 0)
        elif padding == 'same':
            PADL = int(math.floor((EKW - 1)/2))
            PADT = int(math.floor((EKH - 1)/2))
            PADR = int(math.ceil((EKW - 1)/2))
            PADB = int(math.ceil((EKH - 1)/2))
            OH_T = H * stride
            OW_T = W * stride
        elif isinstance(padding, int):
            PADL = PADT = PADR = PADB = padding
        elif isinstance(padding, Iterable):
            padding = tuple(int(x) for x in padding)
            if len(padding) != 4:
                raise ValueError("Invalid paddings list length.")
            PADL, PADT, PADR, PADB = padding
        else:
            raise ValueError("Invalid padding value.")

        self.PADL = PADL
        self.PADT = PADT
        self.PADR = PADR
        self.PADB = PADB

        self.OH = max(1, int((H + PADT + PADB - EKH) / stride + 1) )
        self.OW = max(1, int((W + PADL + PADR - EKW) / stride + 1) )
        self.OH_T = OH_T
        self.OW_T = OW_T


