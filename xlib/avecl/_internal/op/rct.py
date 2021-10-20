import numpy as np

from ..Tensor import Tensor
from .any_wise import any_wise, sqrt
from .concat import concat
from .cvt_color import cvt_color
from .slice_ import split
from .reduce import moments


def rct(target_t : Tensor, source_t : Tensor, target_mask_t : Tensor = None, source_mask_t : Tensor = None, mask_cutoff = 0.5) -> Tensor:
    """
    Transfer color using rct method.

    arguments

        target_t    Tensor( [N]CHW ) C==3 (BGR) float16|32

        source_t    Tensor( [N]CHW ) C==3 (BGR) float16|32

        target_mask_t(None)   Tensor( [N]CHW ) C==1|3 float16|32

        target_source_t(None) Tensor( [N]CHW ) C==1|3 float16|32

    reference: Color Transfer between Images https://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf
    """
    
    if target_t.ndim != source_t.ndim:
        raise ValueError('target_t.ndim != source_t.ndim')
    
    if target_t.ndim == 3:    
        ch_axis = 0
        spatial_axes = (1,2) 
    else:
        ch_axis = 1
        spatial_axes = (2,3) 
    
    target_t = cvt_color(target_t, 'BGR', 'LAB', ch_axis=ch_axis)
    source_t = cvt_color(source_t, 'BGR', 'LAB', ch_axis=ch_axis)

    target_stat_t = target_t
    if target_mask_t is not None:
        target_stat_t = any_wise('O = I0*(I1 >= I2)', target_stat_t, target_mask_t, np.float32(mask_cutoff) )

    source_stat_t = source_t
    if source_mask_t is not None:
        source_stat_t = any_wise('O = I0*(I1 >= I2)', source_stat_t, source_mask_t, np.float32(mask_cutoff) )

    target_stat_mean_t, target_stat_var_t = moments(target_stat_t, axes=spatial_axes)
    source_stat_mean_t, source_stat_var_t = moments(source_stat_t, axes=spatial_axes)
    
    target_t = any_wise(f"""
O_0 = clamp( (I0_0 - I1_0) * sqrt(I2_0) / sqrt(I3_0) + I4_0, 0.0, 100.0);
O_1 = clamp( (I0_1 - I1_1) * sqrt(I2_1) / sqrt(I3_1) + I4_1, -127.0, 127.0);
O_2 = clamp( (I0_2 - I1_2) * sqrt(I2_2) / sqrt(I3_2) + I4_2, -127.0, 127.0);
""", target_t, target_stat_mean_t, source_stat_var_t, target_stat_var_t, source_stat_mean_t, 
     dim_wise_axis=ch_axis)
    
    return cvt_color(target_t, 'LAB', 'BGR', ch_axis=ch_axis)