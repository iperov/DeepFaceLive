import cv2
import numpy as np
import numpy.linalg as npla
import math

class Affine2DMat(np.ndarray):
    """
    affine transformation matrix for 2D
    shape is (2,3)
    """

    def __new__(cls, values):
        values = np.array(values)
        if values.shape != (2,3):
            raise ValueError('values must have shape (2,3)')

        obj = super().__new__(cls, shape=(2,3), dtype=np.float32, buffer=None, offset=0, strides=None, order=None)
        obj[:] = values

        return obj

    def __init__(self, values):
        super().__init__()

    def __rmul__(self, other) -> 'Affine2DMat':
        if isinstance(other, Affine2DMat):
            return Affine2DMat( np.matmul( np.concatenate( [ other, [[0,0,1]] ], 0),
                                           np.concatenate( [ self,  [[0,0,1]] ], 0) )[:2] )
        raise ValueError('You can multiplacte Affine2DMat only with Affine2DMat')

    def __mul__(self, other) -> 'Affine2DMat':
        if isinstance(other, Affine2DMat):
            return Affine2DMat( np.matmul( np.concatenate( [ self, [[0,0,1]] ], 0),
                                           np.concatenate( [ other,  [[0,0,1]] ], 0) )[:2] )
        raise ValueError('You can multiplacte Affine2DMat only with Affine2DMat')

    @staticmethod
    def identity():
        return Affine2DMat([[1,0,0],[0,1,0]])

    @staticmethod
    def umeyama(src, dst, estimate_scale=True):
        """
        Estimate N-D similarity transformation with or without scaling.
        Parameters
        ----------
        src : (M, N) array
            Source coordinates.
        dst : (M, N) array
            Destination coordinates.
        estimate_scale : bool
            Whether to estimate scaling factor.

        Returns
        -------
            The homogeneous similarity transformation matrix. The matrix contains
            NaN values only if the problem is not well-conditioned.

        Reference
        Least-squares estimation of transformation parameters between two point patterns", Shinji Umeyama, PAMI 1991, DOI: 10.1109/34.88573
        """
        num = src.shape[0]
        dim = src.shape[1]

        # Compute mean of src and dst.
        src_mean = src.mean(axis=0)
        dst_mean = dst.mean(axis=0)

        # Subtract mean from src and dst.
        src_demean = src - src_mean
        dst_demean = dst - dst_mean

        # Eq. (38).
        A = np.dot(dst_demean.T, src_demean) / num

        # Eq. (39).
        d = np.ones((dim,), dtype=np.double)
        if np.linalg.det(A) < 0:
            d[dim - 1] = -1

        T = np.eye(dim + 1, dtype=np.double)

        U, S, V = np.linalg.svd(A)

        # Eq. (40) and (43).
        rank = np.linalg.matrix_rank(A)
        if rank == 0:
            return np.nan * T
        elif rank == dim - 1:
            if np.linalg.det(U) * np.linalg.det(V) > 0:
                T[:dim, :dim] = np.dot(U, V)
            else:
                s = d[dim - 1]
                d[dim - 1] = -1
                T[:dim, :dim] = np.dot(U, np.dot(np.diag(d), V))
                d[dim - 1] = s
        else:
            T[:dim, :dim] = np.dot(U, np.dot(np.diag(d), V))

        if estimate_scale:
            # Eq. (41) and (42).
            scale = 1.0 / src_demean.var(axis=0).sum() * np.dot(S, d)
        else:
            scale = 1.0

        T[:dim, dim] = dst_mean - scale * np.dot(T[:dim, :dim], src_mean.T)
        T[:dim, :dim] *= scale

        return Affine2DMat(T[:2])

    @staticmethod
    def from_transformation(cx : float, cy : float,rot_deg : float, scale : float,  tx : float, ty : float) -> 'Affine2DMat':
        """
         cx, cy     center x,y to rotate and scale around this point

         tx, ty     additional translate x,y
        """
        rot_rad = rot_deg * math.pi / 180.0
        alpha = math.cos(rot_rad)*scale
        beta  = math.sin(rot_rad)*scale

        return Affine2DMat( ((alpha, beta,  (1-alpha)*cx - beta*cy + tx),
                             (-beta, alpha, beta*cx + (1-alpha)*cy + ty)) )


    @staticmethod
    def from_3_pairs(src_pts, dst_pts) -> 'Affine2DMat':
        """
        calculates Affine2DMat from three pairs of the corresponding points.
        """
        return Affine2DMat(cv2.getAffineTransform(np.float32(src_pts), np.float32(dst_pts)))

    def invert(self):
        """
        returns inverted Affine2DMat
        """
        ((a, b, c),
         (d, e, f)) = self
        D = a*e - b*d
        D = 1.0 / D if D != 0.0 else 0.0
        a, b, c, d, e, f = ( e*D, -b*D, (b*f-e*c)*D ,
                            -d*D,  a*D, (d*c-a*f)*D )

        return Affine2DMat( ((a, b, c),
                             (d, e, f)) )

    def transform_points(self, points):
        if not isinstance(points, np.ndarray):
            points = np.float32(points)

        dtype = points.dtype

        points = np.pad(points, ((0,0), (0,1) ), constant_values=(1,), mode='constant')

        return np.matmul( np.concatenate( [ self, [[0,0,1]] ], 0), points.T).T[:,:2].astype(dtype)

    def as_uni_mat(self) -> 'Affine2DUniMat':
        """
        represent this mat as Affine2DUniMat
        """
        return Affine2DUniMat(self)


class Affine2DUniMat(Affine2DMat):
    """
    same as Affine2DMat but for transformation of uniform coordinates
    """
    def __rmul__(self, other) -> 'Affine2DUniMat':
        return super().__rmul__(other).as_uni_mat()

    def __mul__(self, other) -> 'Affine2DUniMat':
        return super().__mul__(other).as_uni_mat()

    @staticmethod
    def identity(): return Affine2DMat.identity().as_uni_mat()

    @staticmethod
    def umeyama(src, dst, estimate_scale=True): return Affine2DMat.umeyama(src, dst, estimate_scale=estimate_scale).as_uni_mat()

    @staticmethod
    def from_transformation(cx : float, cy : float,rot_deg : float, scale : float,  tx : float, ty : float) -> 'Affine2DUniMat':
        """
         cx, cy     center x,y to rotate and scale around this point

         tx, ty     additional translate x,y
        """
        return Affine2DMat.from_transformation(cx, cy, rot_deg, scale, tx, ty).as_uni_mat()

    @staticmethod
    def from_3_pairs(src_pts, dst_pts) -> 'Affine2DUniMat': return Affine2DMat.from_3_pairs(src_pts, dst_pts).as_uni_mat()

    def invert(self) -> 'Affine2DUniMat': return super().invert().as_uni_mat()

    def source_scaled_around_center(self, sw : float, sh: float) -> 'Affine2DUniMat':
        """
        produces scaled UniMat around center in source space

            sw, sh      source width/height scale
        """
        src_pts = np.float32([(0,0),(1,0),(0,1)])

        dst_pts = self.transform_points(src_pts)

        src_pts = (src_pts-0.5)/(sw,sh)+0.5

        return Affine2DUniMat.from_3_pairs(src_pts, dst_pts)

    def source_translated(self, utw : float, uth: float) -> 'Affine2DUniMat':
        """
        produces translated UniMat in source space

            utw, uth      uniform translate values
        """
        src_pts = np.float32([(0,0),(1,0),(0,1)])
        dst_pts = self.transform_points(src_pts)
        src_pts += (utw, uth)
        return Affine2DUniMat.from_3_pairs(src_pts, dst_pts)

    def to_exact_mat(self, sw : float, sh: float, tw: float, th: float) -> 'Affine2DMat':
        """
        calculate exact Affine2DMat using provided source and target sizes

            sw, sh      source width/height
            tw, th      target width/height
        """
        return Affine2DMat.from_3_pairs([[0,0],[sw,0],[0,sh]],
                                        self.transform_points( [(0,0),(1,0),(0,1)] ) * (tw,th) )



# def scaled(self, sw : float, sh: float, tw: float, th: float) -> 'Affine2DMat':
#     """

#         sw, sh      source width/height scale
#         tw, th      target width/height scale
#     """
#     src_pts = np.float32([(0,0),(1,0),(0,1),(0.5,0.5)])
#     src_pts -= 0.5

#     dst_pts = self.transform_points(src_pts)

#     print(src_pts, dst_pts)

#     src_pts = src_pts*(sw,sh)

#     dst_cpt = dst_pts[-1]

#     dst_pts = (dst_pts-dst_cpt)*(tw,th) + dst_cpt*(tw,th)



#     return Affine2DUniMat.from_3_pairs(src_pts[:3], dst_pts[:3] )
