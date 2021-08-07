from typing import List, Union

from xlib import math as lib_math

from .FaceULandmarks import FaceULandmarks
from .FaceURect import FaceURect
from .FacePose import FacePose

class _part_picklable_expandable:
    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

class _part_image_name:
    def __init__(self):
        self._image_name : Union[str, None] = None

    def get_image_name(self) -> Union[str, None]: return self._image_name
    def set_image_name(self, image_name : Union[str, None]):
        if image_name is not None and not isinstance(image_name, str):
            raise ValueError(f'image_name must be an instance of str or None')
        self._image_name = image_name

class _part_person_name:
    def __init__(self):
        self._person_name : Union[str, None] = None

    def get_person_name(self) -> Union[str, None]: return self._person_name
    def set_person_name(self, person_name : Union[str, None]):
        if person_name is not None and not isinstance(person_name, str):
            raise ValueError(f'person_name must be an instance of str or None')
        self._person_name = person_name

class _part_face_align:
    def __init__(self):
        self._face_align : Union['FaceAlign', None] = None

    def get_face_align(self) -> Union['FaceAlign', None]: return self._face_align
    def set_face_align(self, face_align : 'FaceAlign'):
        """add FaceAlign"""
        if not isinstance(face_align, FaceAlign):
            raise ValueError('face_align must be an instance of FaceAlign')
        self._face_align = face_align

class _part_face_urect:
    def __init__(self):
        self._face_urect : Union[FaceURect, None] = None

    def get_face_urect(self) -> Union['FaceURect', None]:
        """get uniform FaceURect"""
        return self._face_urect

    def set_face_urect(self, face_urect : Union['FaceURect', None]):
        if face_urect is not None and not isinstance(face_urect, FaceURect):
            raise ValueError(f'face_urect must be an instance of FaceURect or None')
        self._face_urect = face_urect

class _part_face_ulandmarks_list:
    def __init__(self):
        self._face_ulmrks_list : List[FaceULandmarks] = []

    def get_face_ulandmarks_list(self) -> List['FaceULandmarks']: return self._face_ulmrks_list
    def get_face_ulandmarks_by_type(self, type : 'FaceULandmarks.Type') -> Union['FaceULandmarks', None]:
        """get FaceULandmarks from list by type"""
        if not isinstance(type, FaceULandmarks.Type):
            raise ValueError(f'type must be an instance of FaceULandmarks.Type')

        for ulmrks in self._face_ulmrks_list:
            if ulmrks.get_type() == type:
                return ulmrks
        return None


    def add_face_ulandmarks(self, face_ulmrks : 'FaceULandmarks'):
        if not isinstance(face_ulmrks, FaceULandmarks):
            raise ValueError('face_ulmrks must be an instance of FaceULandmarks')

        if self.get_face_ulandmarks_by_type(face_ulmrks.get_type()) is not None:
            raise Exception(f'_face_ulmrks_list already contains type {face_ulmrks.get_type()}.')

        self._face_ulmrks_list.append(face_ulmrks)

class _part_source_source_face_ulandmarks_type:
    def __init__(self):
        self._source_face_ulandmarks_type : Union[FaceULandmarks.Type, None] = None

    def get_source_face_ulandmarks_type(self) -> Union[FaceULandmarks.Type, None]: return self._source_face_ulandmarks_type
    def set_source_face_ulandmarks_type(self, source_face_ulandmarks_type : Union[FaceULandmarks.Type, None]):
        if source_face_ulandmarks_type is not None and not isinstance(source_face_ulandmarks_type, FaceULandmarks.Type):
            raise ValueError('source_face_ulandmarks_type must be an instance of FaceULandmarks.Type')
        self._source_face_ulandmarks_type = source_face_ulandmarks_type


class _part_coverage:
    def __init__(self):
        self._coverage : Union[float, None] = None

    def get_coverage(self) -> Union[float, None]: return self._coverage
    def set_coverage(self, coverage : Union[float, None]):
        if coverage is not None and not isinstance(coverage, float):
            raise ValueError('coverage must be an instance of float')
        self._coverage = coverage

class _part_source_to_aligned_uni_mat:
    def __init__(self):
        self._source_to_aligned_uni_mat : Union[lib_math.Affine2DUniMat, None] = None

    def get_source_to_aligned_uni_mat(self) -> Union[lib_math.Affine2DUniMat, None]: return self._source_to_aligned_uni_mat
    def set_source_to_aligned_uni_mat(self, source_to_aligned_uni_mat : Union[lib_math.Affine2DUniMat, None]):
        if source_to_aligned_uni_mat is not None and not isinstance(source_to_aligned_uni_mat, lib_math.Affine2DUniMat):
            raise ValueError('source_to_aligned_uni_mat must be an instance of lib_math.Affine2DUniMat')
        self._source_to_aligned_uni_mat = source_to_aligned_uni_mat


class _part_face_mask:
    def __init__(self):
        self._face_mask : Union['FaceMask', None] = None

    def get_face_mask(self) -> Union['FaceMask', None]: return self._face_mask
    def set_face_mask(self, face_mask : 'FaceMask'):
        if not isinstance(face_mask, FaceMask):
            raise ValueError('face_mask must be an instance of FaceMask')
        self._face_mask = face_mask

class _part_face_swap:
    def __init__(self):
        self._face_swap : Union['FaceSwap', None] = None

    def get_face_swap(self) -> Union['FaceSwap', None]: return self._face_swap
    def set_face_swap(self, face_swap : 'FaceSwap'):
        if not isinstance(face_swap, FaceSwap):
            raise ValueError('face_swap must be an instance of FaceSwap')
        self._face_swap = face_swap

class _part_face_pose:
    def __init__(self):
        self._face_pose : Union['FacePose', None] = None

    def get_face_pose(self) -> Union['FacePose', None]: return self._face_pose
    def set_face_pose(self, face_pose : 'FacePose'):
        if not isinstance(face_pose, FacePose):
            raise ValueError('face_pose must be an instance of FacePose')
        self._face_pose = face_pose


class FaceMark(_part_picklable_expandable,
                _part_image_name,
                _part_person_name,
                _part_face_urect,
                _part_face_ulandmarks_list,
                _part_face_align,
                _part_face_pose,
                ):
    """
    Describes meta data of single face.

    must not contain any images or large buffers, only references or filenames of them.
    """
    def __init__(self):
        _part_image_name.__init__(self)
        _part_person_name.__init__(self)
        _part_face_urect.__init__(self)
        _part_face_ulandmarks_list.__init__(self)
        _part_face_align.__init__(self)
        _part_face_pose.__init__(self)

class FaceAlign(_part_picklable_expandable,
                _part_image_name,
                _part_person_name,
                _part_face_urect,
                _part_face_ulandmarks_list,
                _part_coverage,
                _part_source_source_face_ulandmarks_type,
                _part_source_to_aligned_uni_mat,
                _part_face_mask,
                _part_face_swap,
                ):
    def __init__(self):
        _part_image_name.__init__(self)
        _part_person_name.__init__(self)
        _part_coverage.__init__(self)
        _part_source_source_face_ulandmarks_type.__init__(self)
        _part_source_to_aligned_uni_mat.__init__(self)
        _part_face_urect.__init__(self)
        _part_face_ulandmarks_list.__init__(self)
        _part_face_mask.__init__(self)
        _part_face_swap.__init__(self)


class FaceSwap(_part_picklable_expandable,
               _part_image_name,
               _part_person_name,
               _part_face_mask,
              ):

    def __init__(self):
        _part_image_name.__init__(self)
        _part_person_name.__init__(self)
        _part_face_mask.__init__(self)


class FaceMask(_part_picklable_expandable,
               _part_image_name,
              ):
    def __init__(self):
        _part_image_name.__init__(self)


