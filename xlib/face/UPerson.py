import uuid
from typing import Union

from .IState import IState


class UPerson(IState):
    def __init__(self):
        """
        """
        self._uuid : Union[bytes, None] = None
        self._name : Union[str, None] = None
        self._age : Union[int, None] = None

    def __str__(self): return f"UPerson UUID:[...{self._uuid[-4:].hex()}] name:[{self._name}] age:[{self._age}]"
    def __repr__(self): return self.__str__()

    @staticmethod
    def from_state(state : dict) -> 'UPerson':
        ufm = UPerson()
        ufm.restore_state(state)
        return ufm
        
    def restore_state(self, state : dict):
        self._uuid = state.get('_uuid', None)
        self._name = state.get('_name', None)
        self._age = state.get('_age', None)

    def dump_state(self) -> dict:
        return {'_uuid' : self._uuid,
                '_name' : self._name,
                '_age' : self._age,
                }

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

    def get_age(self) -> Union[str, None]: return self._age
    def set_age(self, age : Union[int, None]):
        if age is not None and not isinstance(age, int):
            raise ValueError(f'age must be an instance of int or None')
        self._age = age
