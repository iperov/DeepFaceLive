import numpy as np
import numpy.linalg as npla


def segment_length(p1 : np.ndarray, p2 : np.ndarray):
    """
        p1  (2,)
        p2  (2,)
    """
    return npla.norm(p2-p1)

def segment_to_vector(p1 : np.ndarray, p2 : np.ndarray):
    """
        p1  (2,)
        p2  (2,)
    """
    x = p2-p1
    x /= npla.norm(x)
    return x


def intersect_two_line(a1, a2, b1, b2) -> np.ndarray:
    """
    Returns the point of intersection of the lines (not segments) passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return (float('inf'), float('inf'))
    return np.array( [x/z, y/z], np.float32 )

def polygon_area(poly : np.ndarray) -> float:
    """
    calculate area of n-vertices polygon with non intersecting edges

        poly   np.ndarray (n,2)
    """
    return float( np.abs(np.sum( poly[:,0] * np.roll( poly[:,1], -1  ) - poly[:,1] * np.roll( poly[:,0], -1  )  ) / 2) )

