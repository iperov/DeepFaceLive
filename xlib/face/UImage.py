import uuid
from typing import Union

import numpy as np

from .IState import IState


class UImage(IState):

    def __init__(self):
        """
        represents uncompressed image uint8 HWC ( 1/3/4 channels )
        """
        self._uuid : Union[bytes, None] = None
        self._name : Union[str, None] = None
        self._image : np.ndarray = None

    def __str__(self): return f"UImage UUID:[...{self.get_uuid()[-4:].hex()}] name:[{self._name}] image:[{ (self._image.shape, self._image.dtype) if self._image is not None else None}]"
    def __repr__(self): return self.__str__()
    
    @staticmethod
    def from_state(state : dict) -> 'UImage':
        ufm = UImage()
        ufm.restore_state(state)
        return ufm
        
    def restore_state(self, state : dict):
        self._uuid = state.get('_uuid', None)
        self._name = state.get('_name', None)
        self._image = state.get('_image', None)

    def dump_state(self, exclude_image=False) -> dict:
        d =  {'_uuid' : self._uuid,
              '_name' : self._name,
              }
              
        if not exclude_image:
            d['_image'] = self._image
            
        return d
                
    def get_uuid(self) -> Union[bytes, None]:
        if self._uuid is None:
            self._uuid = uuid.uuid4().bytes
        return self._uuid

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

