import cv2
import numpy as np
import numpy.linalg as npla

def sot(src,trg, mask=None, steps=10, batch_size=30, reg_sigmaXY=16.0, reg_sigmaV=5.0, return_diff=False):
    """
    Color Transform via Sliced Optimal Transfer, ported from https://github.com/dcoeurjo/OTColorTransfer

    src         - any float range any channel image
    dst         - any float range any channel image, same shape as src
    mask        - 
    
    steps       - number of solver steps
    batch_size  - solver batch size
    reg_sigmaXY - apply regularization and sigmaXY of filter, otherwise set to 0.0
    reg_sigmaV  - sigmaV of filter

    return value - clip it manually
    
    TODO check why diff result on float and uint8 images
    """
    if not np.issubdtype(src.dtype, np.floating):
        raise ValueError("src value must be float")
    if not np.issubdtype(trg.dtype, np.floating):
        raise ValueError("trg value must be float")

    if len(src.shape) != 3:
        raise ValueError("src shape must have rank 3 (h,w,c)")

    if src.shape != trg.shape:
        raise ValueError("src and trg shapes must be equal")

    src_dtype = src.dtype
    h,w,c = src.shape
    new_src = src.copy()

    advect = np.empty ( (h*w,c), dtype=src_dtype )
    for step in range (steps):
        advect.fill(0)
        for batch in range (batch_size):
            dir = np.random.normal(size=c).astype(src_dtype)
            dir /= npla.norm(dir)

            projsource = np.sum( new_src*dir*mask, axis=-1).reshape ((h*w))
            projtarget = np.sum( trg*dir*mask, axis=-1).reshape ((h*w))

            idSource = np.argsort (projsource)
            idTarget = np.argsort (projtarget)

            a = projtarget[idTarget]-projsource[idSource]
            for i_c in range(c):
                advect[idSource,i_c] += a * dir[i_c]
                
        new_src += (advect.reshape( (h,w,c) ) * mask) / batch_size

    if reg_sigmaXY != 0.0:
        src_diff = new_src-src
        src_diff_filt = cv2.bilateralFilter (src_diff, 0, reg_sigmaV, reg_sigmaXY )
        if len(src_diff_filt.shape) == 2:
            src_diff_filt = src_diff_filt[...,None]
        if return_diff:
            return src_diff_filt
        return src + src_diff_filt
    else:
        if return_diff:
            return new_src-src
        return new_src
