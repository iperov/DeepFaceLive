from typing import Iterable, Tuple, Union

import cv2
import numpy as np

from ..math import Affine2DMat, Affine2DUniMat

class FaceWarper:
    def __init__(self,
                 img_to_face_uni_mat : Affine2DUniMat,

                 align_rot_deg : Union[None, float,  Tuple[float, float] ] = [-15,15],
                 align_scale : Union[None, float,  Tuple[float, float] ]   = [-0.15, 0.15],
                 align_tx : Union[None, float,  Tuple[float, float] ]      = [-0.05, 0.05],
                 align_ty : Union[None, float,  Tuple[float, float] ]      = [-0.05, 0.05],

                 rw_grid_cell_count : Union[None, int,  Tuple[int, int] ]    = [3,7],
                 rw_grid_rot_deg : Union[None, float,  Tuple[float, float] ] = [-180,180],
                 rw_grid_scale : Union[None, float,  Tuple[float, float] ]   = [-0.25, 0.25],
                 rw_grid_tx : Union[None, float,  Tuple[float, float] ]      = [-0.25, 0.25],
                 rw_grid_ty : Union[None, float,  Tuple[float, float] ]      = [-0.25, 0.25],

                 rnd_state : np.random.RandomState = None,
                ):
        """
        Max quality one-pass face augmentation via geometric transformations with provided random range or exact values.
        
            img_to_face_uni_mat    Affine2DUniMat
            
        Affine2DUniMat given from FLandmarks2D.calc_cut
        it is an uniform affineMat to transform original image to aligned face

            align_* rw_grid_*   
        
        exact augmentation parameters or range for random generation.
        """
        self._img_to_face_uni_mat = img_to_face_uni_mat
        self._face_to_img_uni_mat = img_to_face_uni_mat.invert()

        rnd_state = np.random.RandomState()
        rnd_state.set_state(rnd_state.get_state() if rnd_state is not None else np.random.RandomState().get_state())
        
        self._align_rot_deg      = rnd_state.uniform(*align_rot_deg) if isinstance(align_rot_deg, Iterable) else align_rot_deg
        self._align_scale        = rnd_state.uniform(*align_scale) if isinstance(align_scale, Iterable) else align_scale
        self._align_tx           = rnd_state.uniform(*align_tx) if isinstance(align_tx, Iterable) else align_tx
        self._align_ty           = rnd_state.uniform(*align_ty) if isinstance(align_ty, Iterable) else align_ty
        self._rw_grid_cell_count = rnd_state.randint(*rw_grid_cell_count) if isinstance(rw_grid_cell_count, Iterable) else rw_grid_cell_count
        self._rw_grid_rot_deg    = rnd_state.uniform(*rw_grid_rot_deg) if isinstance(rw_grid_rot_deg, Iterable) else rw_grid_rot_deg
        self._rw_grid_scale      = rnd_state.uniform(*rw_grid_scale) if isinstance(rw_grid_scale, Iterable) else rw_grid_scale
        self._rw_grid_tx         = rnd_state.uniform(*rw_grid_tx) if isinstance(rw_grid_tx, Iterable) else rw_grid_tx
        self._rw_grid_ty         = rnd_state.uniform(*rw_grid_ty) if isinstance(rw_grid_ty, Iterable) else rw_grid_ty
        
        self._warp_rnd_mat = Affine2DUniMat.from_transformation(0.5, 0.5, self._rw_grid_rot_deg, 1.0+self._rw_grid_scale, self._rw_grid_tx, self._rw_grid_ty)
        self._align_rnd_mat = Affine2DUniMat.from_transformation(0.5, 0.5, self._align_rot_deg, 1.0+self._align_scale, self._align_tx, self._align_ty)
        
        self._rnd_state_state = rnd_state.get_state()
        self._cached = {}
        
    def get_aligned_random_transform_mat(self) -> Affine2DUniMat:
        """
        returns Affine2DUniMat that represents transformation from aligned face to randomly transformed aligned face
        """
        mat1 = self._img_to_face_uni_mat
        mat2 = (self._face_to_img_uni_mat * self._align_rnd_mat).invert()
        
        pts = [ [0,0], [1,0], [1,1]]
        src_pts = mat1.transform_points(pts)
        dst_pts = mat2.transform_points(pts)
        
        return Affine2DUniMat.from_3_pairs(src_pts, dst_pts)
        
    def transform(self, img : np.ndarray, out_res : int, random_warp : bool = True) -> np.ndarray:
        """
        transform an image. 
        
        Subsequent calls will output the same result for any img shape and out_res.
        
            img                 np.ndarray  (HWC)
            
            out_res             int
            
            random_warp(True)   bool
        """
        H,W = img.shape[:2]

        key = (H,W,random_warp)
        data = self._cached.get(key, None)
        if data is None:
            rnd_state = np.random.RandomState()
            rnd_state.set_state( self._rnd_state_state )
            self._cached[key] = data = self._gen(H,W, random_warp, out_res, rnd_state=rnd_state )
            
        image_grid, face_mask = data
            
        new_img = cv2.remap(img, image_grid, None, interpolation=cv2.INTER_LANCZOS4)
        new_img *= face_mask
        return new_img
        
    def _gen(self, H, W, random_warp, out_res, rnd_state):
        """generate grid and mask"""
        
        # make identity grid
        image_grid = np.stack(np.meshgrid(np.linspace(0., 1.0, H, dtype=np.float32),
                                          np.linspace(0., 1.0, W, dtype=np.float32)), -1)
        
        if random_warp:
            # make a random face_warp_grid in the space of the face
            face_warp_grid = FaceWarper._gen_random_warp_uni_grid_diff(out_res, self._rw_grid_cell_count, 0.12, rnd_state)

            # apply random transformation mat of face_warp_grid to mat that transforms face to image
            face_warp_grid_uni_mat = self._face_to_img_uni_mat * self._warp_rnd_mat

            # warp face_warp_grid to the space of image using previous mat and merge with image_grid
            image_grid += cv2.warpAffine(face_warp_grid, face_warp_grid_uni_mat.to_exact_mat(out_res,out_res, W, H), (W,H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        # scale uniform grid to image size
        image_grid *= (H-1, W-1)

        # apply random transformations for align mat
        img_to_face_rnd_mat = (self._face_to_img_uni_mat * self._align_rnd_mat).invert().to_exact_mat(W,H,out_res,out_res)

        # warp image_grid to face space
        image_grid = cv2.warpAffine(image_grid, img_to_face_rnd_mat, (out_res,out_res), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE )

        # make mask to refine image-boundary visible in face space
        face_mask = cv2.warpAffine( np.ones( (H,W), dtype=np.uint8), img_to_face_rnd_mat, (out_res,out_res), flags=cv2.INTER_NEAREST)[...,None]

        return image_grid, face_mask
        
    def _gen_random_warp_uni_grid_diff(size: int, cell_count, cell_mod, rnd_state) -> np.ndarray:
        """
        generates square uniform random warp coordinate differences
        
        grid of shape (size, size, 2)  (x,y)

        cell_count(3)        3+

        cell_mod  (0.12)     [ 0 .. 0.24 ]
        """
        cell_count = max(3, cell_count)
        cell_mod = np.clip(cell_mod, 0, 0.24)
        cell_size = 1.0 / (cell_count-1)

        grid = np.zeros( (cell_count,cell_count, 2), dtype=np.float32 )

        grid[1:-1,1:-1, 0:2] += rnd_state.uniform (low=-cell_size*cell_mod, high=cell_size*cell_mod, size=(cell_count-2, cell_count-2, 2) )
        grid = cv2.resize(grid, (size, size), interpolation=cv2.INTER_CUBIC ).astype(np.float32)

        # Linear dump border cells to zero
        border_size = size // cell_count
        dumper = np.linspace(0, 1, border_size, dtype=np.float32)
        grid[:border_size, :,:] *= dumper[:,None,None]
        grid[-border_size:,:,:] *= dumper[::-1,None,None]
        grid[:,:border_size ,:] *= dumper[None,:,None]
        grid[:,-border_size:,:] *= dumper[None,::-1,None]

        return grid
