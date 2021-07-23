class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

from .EventListener import EventListener

def all_is_not_None(*args): return all(x is not None for x in args)
def all_is_None(*args): return all(x is None for x in args)

class Disposable:
    def __del__(self):
        self.dispose()

    def _on_dispose(self):
        pass


    def dispose(self):
        _disposed = getattr(self, '_disposed', False)
        if not _disposed:
            self._disposed = True
            self._on_dispose()

def repeat_call(obj, func_name, args_list):
    """

    """
    func = getattr(obj, func_name)
    for args in args_list:
        if not isinstance(args, list):
            args = [args]
        func(*args)

def repeat_objs_call(obj_list, func_name, *args, **kwargs):
    """

    """
    for obj in obj_list:
        func = getattr(obj, func_name)
        func(*args, **kwargs)
