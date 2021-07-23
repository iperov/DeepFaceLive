import cv2
import numpy as np


def imread(filepath, flags=cv2.IMREAD_UNCHANGED, loader_func=None, raise_on_error=True) -> np.ndarray:
    """
    same as cv2.imread but allows to open non-english characters path

    arguments

     loader_func(None)    callable    your own loader for filepath
     raise_on_error(True)   if False - no Exception on error, just None return

    returns
        np.ndarray

    raises Exception if error and raise_on_error
    """
    try:
        if loader_func is not None:
            bytes = bytearray(loader_func(filepath))
        else:
            with open(filepath, "rb") as stream:
                bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        return cv2.imdecode(numpyarray, flags)
    except Exception as e:
        if raise_on_error:
            raise e
        return None

def imwrite(filepath, img, *args):
    ret, buf = cv2.imencode(filepath.suffix, img, *args)
    if ret == True:
        try:
            with open(filepath, "wb") as stream:
                stream.write( buf )
        except:
            pass
