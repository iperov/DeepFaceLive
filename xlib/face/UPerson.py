import uuid
from typing import Union


class UPerson:
    def __init__(self, _from_pickled=False):
        """
        """
        self._uuid : Union[bytes, None] = uuid.uuid4().bytes_le if not _from_pickled else None
        self._name : Union[str, None] = None
        self._age : Union[int, None] = None

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__(_from_pickled=True)
        self.__dict__.update(d)

    def __str__(self): return f"UPerson UUID:[...{self._uuid[-4:].hex()}] name:[{self._name}] age:[{self._age}]"
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

    def get_age(self) -> Union[str, None]: return self._age
    def set_age(self, age : Union[int, None]):
        if age is not None and not isinstance(age, int):
            raise ValueError(f'age must be an instance of int or None')
        self._age = age