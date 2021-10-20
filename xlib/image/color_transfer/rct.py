import cv2
import numpy as np
import numexpr as ne

def rct(target : np.ndarray, source : np.ndarray, target_mask : np.ndarray = None, source_mask : np.ndarray = None, mask_cutoff=0.5) -> np.ndarray:
    """
    Transfer color using rct method.

        target      np.ndarray H W 3C   (BGR)   np.float32
        source      np.ndarray H W 3C   (BGR)   np.float32

        target_mask(None)   np.ndarray H W 1C  np.float32
        source_mask(None)   np.ndarray H W 1C  np.float32
        
        mask_cutoff(0.5)    float

    masks are used to limit the space where color statistics will be computed to adjust the target

    reference: Color Transfer between Images https://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf
    """
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB)

    source_input = source
    if source_mask is not None:
        source_input = source_input.copy()
        source_input[source_mask[...,0] < mask_cutoff] = [0,0,0]
    
    target_input = target
    if target_mask is not None:
        target_input = target_input.copy()
        target_input[target_mask[...,0] < mask_cutoff] = [0,0,0]

    target_l_mean, target_l_std, target_a_mean, target_a_std, target_b_mean, target_b_std, \
        = target_input[...,0].mean(), target_input[...,0].std(), target_input[...,1].mean(), target_input[...,1].std(), target_input[...,2].mean(), target_input[...,2].std()
    
    source_l_mean, source_l_std, source_a_mean, source_a_std, source_b_mean, source_b_std, \
        = source_input[...,0].mean(), source_input[...,0].std(), source_input[...,1].mean(), source_input[...,1].std(), source_input[...,2].mean(), source_input[...,2].std()
    
    # not as in the paper: scale by the standard deviations using reciprocal of paper proposed factor
    target_l = target[...,0]
    target_l = ne.evaluate('(target_l - target_l_mean) * source_l_std / target_l_std + source_l_mean')

    target_a = target[...,1]
    target_a = ne.evaluate('(target_a - target_a_mean) * source_a_std / target_a_std + source_a_mean')
    
    target_b = target[...,2]
    target_b = ne.evaluate('(target_b - target_b_mean) * source_b_std / target_b_std + source_b_mean')

    np.clip(target_l,    0, 100, out=target_l)
    np.clip(target_a, -127, 127, out=target_a)
    np.clip(target_b, -127, 127, out=target_b)

    return cv2.cvtColor(np.stack([target_l,target_a,target_b], -1), cv2.COLOR_LAB2BGR)
