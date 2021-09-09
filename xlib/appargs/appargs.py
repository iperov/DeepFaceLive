import os

def set_arg_str(name : str, value : str):
    os.environ[name] = value
    
def set_arg_bool(name : str, value : bool):
    set_arg_str(name, '1' if value else '0')
    
def get_arg_str(name : str, default = None) -> str:
    return os.environ.get(name, default)
    
def get_arg_bool(name : str, default = False) -> bool:
    x = get_arg_str(name, default=None)
    if x is None:
        return default
    return bool(int(x))
    