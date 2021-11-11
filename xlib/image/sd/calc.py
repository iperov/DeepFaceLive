import numpy as np
import numpy.linalg as npla

def dist_to_edges(pts, pt, is_closed=False):
    """
    returns array of dist from pt to edge and projection pt to edges
    """
    if is_closed:
        a = pts
        b = np.concatenate( (pts[1:,:], pts[0:1,:]), axis=0 )
    else:
        a = pts[:-1,:]
        b = pts[1:,:]

    pa = pt-a
    ba = b-a
    
    div = np.einsum('ij,ij->i', ba, ba)
    div[div==0]=1
    h = np.clip( np.einsum('ij,ij->i', pa, ba) / div, 0, 1 )
    
    x = npla.norm ( pa - ba*h[...,None], axis=1 )
    
    return x, a+ba*h[...,None]
    
