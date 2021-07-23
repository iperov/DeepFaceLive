from collections import Iterable


class EventListener:
    __slots__ = ['_funcs']
    def __init__(self):
        self._funcs = []

    def has_listeners(self):
        return len(self._funcs) != 0

    def add(self, func_or_list):
        if isinstance(func_or_list, Iterable):
            func_or_list = tuple(func_or_list)
        else:
            func_or_list = (func_or_list,)

        for func in func_or_list:
            if func not in self._funcs:
                self._funcs.append(func)

    def call(self, *args, **kwargs):
        for func in self._funcs:
            func(*args, **kwargs)
