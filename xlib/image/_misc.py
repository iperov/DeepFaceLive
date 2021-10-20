import numpy as np

def get_NHWC_shape(img : np.ndarray):
    """
    returns NHWC shape where missed dims are 1
    """
    ndim = img.ndim
    if ndim not in [2,3,4]:
        raise ValueError(f'img.ndim must be 2,3,4, not {ndim}.')

    if ndim == 2:
        N, (H,W), C = 1, img.shape, 1
    elif ndim == 3:
        N, (H,W,C) = 1, img.shape
    else:
        N,H,W,C = img.shape
    return N,H,W,C