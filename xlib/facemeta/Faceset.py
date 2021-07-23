from pathlib import Path
from typing import Tuple

import cv2
from xlib import cv as lib_cv
from xlib import path as lib_path
from xlib.io import FormattedFileIO

from .face import FaceMark


class Faceset:
    """
    Faceset is a class to store and manage multiple FaceMark()'s


    arguments:

     path       path to directory

    raises

     Exception, ValueError
    """

    def __init__(self, path):
        self._path = path = Path(path)
        if not path.is_dir():
            raise ValueError('Path must be a directory.')

        self.reload()

    def reload(self):
        """
        reload the faceset

        raises

        Exception
        """
        self._is_packed = False

        filepaths = lib_path.get_files_paths(self._path)

        face_filepaths = self._face_filepaths = set()

        for filepath in filepaths:
            suffix = filepath.suffix
            if suffix == '.face':
                if self._is_packed:
                    raise Exception(f'{self._path} contains .faceset and .face but only one type is allowed.')

                face_filepaths.add(filepath.name)
            elif suffix == '.faceset':
                if self._is_packed:
                    raise Exception(f'{self._path} contains more than one .faceset.')

                if len(face_filepaths) != 0:
                    raise Exception(f'{self._path} contains .faceset and .face but only one type is allowed.')
                self._is_packed = True

    def pack(self):
        """
        Pack faceset.
        """

    def unpack(self):
        """
        unpack faceset.
        """

    def is_packed(self) -> bool: return self._is_packed

    def get_face_count(self): return len(self._face_filepaths)

    def get_faces(self) -> Tuple[FaceMark]:
        """
        returns a tuple of FaceMark()'s
        """

    def save_face(self, face : FaceMark):
        filepath = self._path / (face.get_name() + '.face')

        with FormattedFileIO(filepath, 'w+') as f:
            f.write_pickled(face)

        self._face_filepaths.add(filepath.name)

    def save_image(self, name, img, type='jpg'):
        filepath = self._path / (name + f'.{type}')

        if type == 'jpg':
            lib_cv.imwrite(filepath, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100] )
        else:
            raise ValueError(f'Unknown type {type}')
