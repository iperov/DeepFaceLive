import uuid
from typing import Union
from enum import IntEnum

class FMask:
    class Type(IntEnum):
        WHOLE_FACE = 0
        
    def __init__(self, _from_pickled=False):
        """
        """
        self._uuid : Union[bytes, None] = uuid.uuid4().bytes if not _from_pickled else None
        self._mask_type : Union[FMask.Type, None] = None
        self._FImage_uuid : Union[bytes, None] = None
        
    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__(_from_pickled=True)
        self.__dict__.update(d)

    def get_uuid(self) -> Union[bytes, None]: return self._uuid
    def set_uuid(self, uuid : Union[bytes, None]):
        if uuid is not None and not isinstance(uuid, bytes):
            raise ValueError(f'uuid must be an instance of bytes or None')
        self._uuid = uuid

    def get_mask_type(self) -> Union['FMask.Type', None]: return self._mask_type
    def set_mask_type(self, mask_type : Union['FMask.Type', None]):
        if mask_type is not None and not isinstance(mask_type, 'FMask.Type'):
            raise ValueError(f'mask_type must be an instance of FMask.Type or None')
        self._mask_type = mask_type
        
    def get_FImage_uuid(self) -> Union[bytes, None]: return self._FImage_uuid
    def set_FImage_uuid(self, FImage_uuid : Union[bytes, None]):
        if FImage_uuid is not None and not isinstance(FImage_uuid, bytes):
            raise ValueError(f'FImage_uuid must be an instance of bytes or None')
        self._FImage_uuid = FImage_uuid
    