from typing import Any, Union

import numpy as np


class IState:
    """
    """
    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

    @staticmethod
    def _dump_IState_obj(obj : Union[Any, None]) -> Union[Any, None]:
        """
        """
        if obj is None:
            return None
        return obj.dump_state()

    @staticmethod
    def _dump_np_array(n : Union[np.ndarray, None] ) -> Union[Any, None]:
        if n is None:
            return None
        return ( n.data.tobytes(), n.dtype, n.shape )

    @staticmethod
    def _dump_enum(enum_obj : Union[Any, None]) -> Union[Any, None]:
        if enum_obj is None:
            return None
        return enum_obj.value

    @staticmethod
    def _restore_IState_obj(cls_, state : Union[Any, None]) -> Union[np.ndarray, None]:
        if state is None:
            return None

        obj = cls_()
        obj.restore_state(state)
        return obj

    @staticmethod
    def _restore_np_array(state : Union[Any, None]) -> Union[np.ndarray, None]:
        if state is None:
            return None
        return np.frombuffer(state[0], dtype=state[1]).reshape(state[2])

    @staticmethod
    def _restore_enum(enum_cls, state : Union[Any, None]) -> Union[Any, None]:
        if state is None:
            return None

        return enum_cls(state)

    def restore_state(self, state : dict):
        """
        """
        raise NotImplementedError()

    def dump_state(self) -> dict:
        """
        returns import-independent state of class in dict
        """
        raise NotImplementedError()

