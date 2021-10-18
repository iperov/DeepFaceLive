import uuid
from typing import List, Tuple, Union

from ..math import Affine2DMat
from .ELandmarks2D import ELandmarks2D
from .EMaskType import EMaskType
from .FLandmarks2D import FLandmarks2D
from .FPose import FPose
from .FRect import FRect


class UFaceMark:
    def __init__(self, _from_pickled=False):
        """
        Describes single face in the image.
        """
        self._uuid : Union[bytes, None] = uuid.uuid4().bytes_le if not _from_pickled else None
        self._UImage_uuid : Union[bytes, None] = None
        self._UPerson_uuid : Union[bytes, None] = None
        self._FRect : Union[FRect, None] = None
        self._FLandmarks2D_list : List[FLandmarks2D] = []
        self._FPose : Union[FPose, None] = None
        self._mask_info_list : List = []
        
    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__(_from_pickled=True)
        self.__dict__.update(d)
        
    def __str__(self): 
        s = "Masks: "
        return f"UFaceMark UUID:[...{self._uuid[-4:].hex()}]"
        
    def __repr__(self): return self.__str__()
    
    def get_uuid(self) -> Union[bytes, None]: return self._uuid
    def set_uuid(self, uuid : Union[bytes, None]):
        if uuid is not None and not isinstance(uuid, bytes):
            raise ValueError(f'uuid must be an instance of bytes or None')
        self._uuid = uuid

    def get_UImage_uuid(self) -> Union[bytes, None]: return self._UImage_uuid
    def set_UImage_uuid(self, UImage_uuid : Union[bytes, None]):
        if UImage_uuid is not None and not isinstance(UImage_uuid, bytes):
            raise ValueError(f'UImage_uuid must be an instance of bytes or None')
        self._UImage_uuid = UImage_uuid

    def get_UPerson_uuid(self) -> Union[bytes, None]: return self._UPerson_uuid
    def set_UPerson_uuid(self, UPerson_uuid : Union[bytes, None]):
        if UPerson_uuid is not None and not isinstance(UPerson_uuid, bytes):
            raise ValueError(f'UPerson_uuid must be an instance of bytes or None')
        self._UPerson_uuid = UPerson_uuid

    def get_FRect(self) -> Union['FRect', None]: return self._FRect
    def set_FRect(self, face_urect : Union['FRect', None]):
        if face_urect is not None and not isinstance(face_urect, FRect):
            raise ValueError(f'face_urect must be an instance of FRect or None')
        self._FRect = face_urect

    def get_all_FLandmarks2D(self) -> List[FLandmarks2D]: return self._FLandmarks2D_list
    def get_FLandmarks2D_by_type(self, type : ELandmarks2D) -> Union[FLandmarks2D, None]:
        """get FLandmarks2D from list by type"""
        if not isinstance(type, ELandmarks2D):
            raise ValueError(f'type must be an instance of ELandmarks2D')

        for ulmrks in self._FLandmarks2D_list:
            if ulmrks.get_type() == type:
                return ulmrks
        return None

    def add_FLandmarks2D(self, flmrks : FLandmarks2D):
        if not isinstance(flmrks, FLandmarks2D):
            raise ValueError('flmrks must be an instance of FLandmarks2D')

        if self.get_FLandmarks2D_by_type(flmrks.get_type()) is not None:
            raise Exception(f'_FLandmarks2D_list already contains type {flmrks.get_type()}.')

        self._FLandmarks2D_list.append(flmrks)

    def get_FPose(self) -> Union[FPose, None]: return self._FPose
    def set_FPose(self, face_pose : FPose):
        if not isinstance(face_pose, FPose):
            raise ValueError('face_pose must be an instance of FPose')
        self._FPose = face_pose

    def get_mask_info_list(self) -> List[Tuple[EMaskType, bytes, Affine2DMat]]:
        return self._mask_info_list
        
    def add_mask_info(self, mask_type : EMaskType, UImage_uuid : bytes, mask_to_mark_uni_mat : Affine2DMat):
        if not isinstance(mask_type, EMaskType):
            raise ValueError('mask_type must be an instance of EMaskType')
        if not isinstance(UImage_uuid, bytes):
            raise ValueError('UImage_uuid must be an instance of bytes')
        if not isinstance(mask_to_mark_uni_mat, Affine2DMat):
            raise ValueError('mask_to_mark_uni_mat must be an instance of Affine2DMat')
            
        self._mask_info_list.append( (mask_type, UImage_uuid, mask_to_mark_uni_mat) )
