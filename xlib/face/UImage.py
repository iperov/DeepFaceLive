import uuid
from typing import Union

import numpy as np

class UImage:

    def __init__(self):
        """
        represents uncompressed image uint8 HWC ( 1/3/4 channels )
        """
        self._uuid : Union[bytes, None] = uuid.uuid4().bytes_le
        self._name : Union[str, None] = None
        self._image : np.ndarray = None

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

    def __str__(self): return f"UImage UUID:[...{self._uuid[-4:].hex()}] name:[{self._name}] image:[{ (self._image.shape, self._image.dtype) if self._image is not None else None}]"
    def __repr__(self): return self.__str__()

    def get_uuid(self) -> Union[bytes, None]: return self._uuid
    def set_uuid(self, uuid : Union[bytes, None]):
        if uuid is not None and not isinstance(uuid, bytes):
            raise ValueError(f'uuid must be an instance of bytes or None')
        self._uuid = uuid

    def get_name(self) -> Union[str, None]: return self._name
    def set_name(self, name : Union[str, None]):
        if name is not None and not isinstance(name, str):
            raise ValueError(f'name must be an instance of str or None')
        self._name = name

    def get_image(self) -> Union[np.ndarray, None]: return self._image
    def assign_image(self, image : Union[np.ndarray, None]):
        """
        assign np.ndarray image , or remove(None)

        It's mean you should not to change provided image nd.array after assigning, or do the copy before.

        Image must be uint8 and HWC 1/3/4 channels.
        """
        if image is not None:
            if image.ndim == 2:
                image = image[...,None]
                
            if image.ndim != 3:
                raise ValueError('image must have ndim == 3')
            _,_,C = image.shape
            if C not in [1,3,4]:
                raise ValueError('image channels must be 1,3,4')
            if image.dtype != np.uint8:
                raise ValueError('image dtype must be uint8')
        self._image = image

