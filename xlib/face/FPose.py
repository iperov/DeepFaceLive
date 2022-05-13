from typing import Tuple

import numpy as np

from .. import math as lib_math
from .IState import IState


class FPose(IState):
    """
    Describes face pitch/yaw/roll
    """
    def __init__(self):
        self._pyr : np.ndarray = None

    def restore_state(self, state : dict):
        self._pyr = IState._restore_np_array(state.get('_pyr', None))

    def dump_state(self) -> dict:
        return {'_pyr' : IState._dump_np_array(self._pyr)}

    def as_radians(self) -> Tuple[float, float, float]:
        """
        returns pitch,yaw,roll in radians
        """
        return self._pyr.copy()

    def as_degress(self) -> Tuple[float, float, float]:
        """
        returns pitch,yaw,roll in degrees
        """
        return np.degrees(self._pyr)

    @staticmethod
    def from_radians(pitch, yaw, roll):
        """
        """
        face_rect = FPose()
        face_rect._pyr = np.array([pitch, yaw, roll], np.float32)
        return face_rect

    @staticmethod
    def from_3D_468_landmarks(lmrks):
        """
        """
        mat = np.empty((3,3))
        mat[0,:] = (lmrks[454] - lmrks[234])/np.linalg.norm(lmrks[454] - lmrks[234])
        mat[1,:] = (lmrks[152] - lmrks[6])/np.linalg.norm(lmrks[152] - lmrks[6])
        mat[2,:] = np.cross(mat[0, :], mat[1, :])
        pitch, yaw, roll = lib_math.rotation_matrix_to_euler(mat)

        return FPose.from_radians(pitch, yaw*2, roll)
