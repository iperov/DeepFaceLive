import pickle
import uuid
from pathlib import Path
from typing import Generator, Iterable, List, Union

import cv2
import h5py
import numpy as np

from .. import console as lib_con
from .FMask import FMask
from .UFaceMark import UFaceMark
from .UImage import UImage
from .UPerson import UPerson


class Faceset:

    def __init__(self, path = None, write_access=False, recreate=False):
        """
        Faceset is a class to store and manage face related data.

        arguments:

            path       path to faceset .dfs file

            write_access

            recreate

        Can be pickled.
        """
        self._f = None

        self._path = path = Path(path)
        if path.suffix != '.dfs':
            raise ValueError('Path must be a .dfs file')

        if path.exists():
            if write_access and recreate:
                path.unlink()
        elif not write_access:
            raise FileNotFoundError(f'File {path} not found.')

        self._mode = 'a' if write_access else 'r'
        self._open()

    def __del__(self):
        self.close()

    def __getstate__(self):
        return {'_path' : self._path, '_mode' : self._mode}

    def __setstate__(self, d):
        self._f = None
        self._path = d['_path']
        self._mode = d['_mode']
        self._open()

    def __repr__(self): return self.__str__()
    def __str__(self):
        return f"Faceset. UImage:{self.get_UImage_count()} UFaceMark:{self.get_UFaceMark_count()} UPerson:{self.get_UPerson_count()}"

    def _open(self):
        if self._f is None:
            self._f = f = h5py.File(self._path, mode=self._mode)
            self._UFaceMark_grp = f.require_group('UFaceMark')
            self._UImage_grp = f.require_group('UImage')
            self._UImage_image_data_grp = f.require_group('UImage_image_data')
            self._UPerson_grp = f.require_group('UPerson')


    def close(self):
        if self._f is not None:
            self._f.close()
            self._f = None

    def optimize(self, verbose=True):
        """
        recreate Faceset with optimized structure.
        """
        if verbose:
            print(f'Optimizing {self._path.name}...')

        tmp_path = self._path.parent / (self._path.stem + '_optimizing' + self._path.suffix)

        tmp_fs = Faceset(tmp_path, write_access=True, recreate=True)
        self._group_copy(tmp_fs._UFaceMark_grp, self._UFaceMark_grp, verbose=verbose)
        self._group_copy(tmp_fs._UPerson_grp, self._UPerson_grp, verbose=verbose)
        self._group_copy(tmp_fs._UImage_grp, self._UImage_grp, verbose=verbose)
        self._group_copy(tmp_fs._UImage_image_data_grp, self._UImage_image_data_grp, verbose=verbose)
        tmp_fs.close()

        self.close()
        self._path.unlink()
        tmp_path.rename(self._path)
        self._open()

    def _group_copy(self, group_dst : h5py.Group, group_src : h5py.Group, verbose=True):
        for key, value in lib_con.progress_bar_iterator(group_src.items(), desc=f'Copying {group_src.name} -> {group_dst.name}', suppress_print=not verbose):
            d = group_dst.create_dataset(key, shape=value.shape, dtype=value.dtype )
            d[:] = value[:]
            for a_key, a_value in value.attrs.items():
                d.attrs[a_key] = a_value

    def _group_read_bytes(self, group : h5py.Group, key : str, check_key=True) -> Union[bytes, None]:
        if check_key and key not in group:
            return None
        dataset = group[key]
        data_bytes = bytearray(len(dataset))
        dataset.read_direct(np.frombuffer(data_bytes, dtype=np.uint8))
        return data_bytes

    def _group_write_bytes(self, group : h5py.Group, key : str, data : bytes, update_existing=True) -> Union[h5py.Dataset, None]:
        if key in group:
            if not update_existing:
                return None
            del group[key]

        return group.create_dataset(key, data=np.frombuffer(data, dtype=np.uint8) )

    ###################
    ### UFaceMark
    ###################
    def add_UFaceMark(self, ufacemark_or_list : UFaceMark, update_existing=True):
        """
        add or update UFaceMark in DB
        """
        if not isinstance(ufacemark_or_list, Iterable):
            ufacemark_or_list : List[UFaceMark] = [ufacemark_or_list]

        for ufm in ufacemark_or_list:
            self._group_write_bytes(self._UFaceMark_grp, ufm.get_uuid().hex(), pickle.dumps(ufm.dump_state()), update_existing=update_existing )

    def get_UFaceMark_count(self) -> int:
        return len(self._UFaceMark_grp.keys())

    def get_all_UFaceMark(self) -> List[UFaceMark]:
        return [ UFaceMark.from_state(pickle.loads(self._group_read_bytes(self._UFaceMark_grp, key, check_key=False))) for key in self._UFaceMark_grp.keys() ]
    
    def get_all_UFaceMark_uuids(self) -> List[bytes]:
        return [ uuid.UUID(key).bytes for key in self._UFaceMark_grp.keys() ]
     
    def get_UFaceMark_by_uuid(self, uuid : bytes) -> Union[UFaceMark, None]:
        data = self._group_read_bytes(self._UFaceMark_grp, uuid.hex())
        if data is None:
            return None
        return UFaceMark.from_state(pickle.loads(data))

    def delete_UFaceMark_by_uuid(self, uuid : bytes) -> bool:
        key = uuid.hex()
        if key in self._UFaceMark_grp:
            del self._UFaceMark_grp[key]
            return True
        return False
    
           
    def iter_UFaceMark(self) -> Generator[UFaceMark, None, None]:
        """
        returns Generator of UFaceMark
        """
        for key in self._UFaceMark_grp.keys():
            yield UFaceMark.from_state(pickle.loads(self._group_read_bytes(self._UFaceMark_grp, key, check_key=False)))

    def delete_all_UFaceMark(self):
        """
        deletes all UFaceMark from DB
        """
        for key in self._UFaceMark_grp.keys():
            del self._UFaceMark_grp[key]

    ###################
    ### UImage
    ###################
    def add_UImage(self, uimage_or_list : UImage, format : str = 'png', quality : int = 100, update_existing=True):
        """
        add or update UImage in DB

         uimage       UImage or list

         format('png')  webp    ( does not support lossless on 100 quality ! )
                        png     ( lossless )
                        jpg
                        jp2 ( jpeg2000 )

         quality(100)   0-100 for formats jpg,jp2,webp
        """
        if format not in ['webp','png', 'jpg', 'jp2']:
            raise ValueError(f'format {format} is unsupported')

        if format in ['jpg','jp2'] and quality < 0 or quality > 100:
            raise ValueError('quality must be in range [0..100]')

        if not isinstance(uimage_or_list, Iterable):
            uimage_or_list : List[UImage] = [uimage_or_list]

        for uimage in uimage_or_list:
            if format == 'webp':
                imencode_args = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
            elif format == 'jpg':
                imencode_args = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            elif format == 'jp2':
                imencode_args = [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), quality*10]
            else:
                imencode_args = []

            ret, data_bytes = cv2.imencode( f'.{format}', uimage.get_image(), imencode_args)
            if not ret:
                raise Exception(f'Unable to encode image format {format}')

            key = uimage.get_uuid().hex()

            self._group_write_bytes(self._UImage_grp, key, pickle.dumps(uimage.dump_state(exclude_image=True)), update_existing=update_existing )
            d = self._group_write_bytes(self._UImage_image_data_grp, key, data_bytes.data, update_existing=update_existing )
            d.attrs['format'] = format
            d.attrs['quality'] = quality

    def get_UImage_count(self) -> int:
        return len(self._UImage_grp.keys())

    def get_all_UImage(self) -> List[UImage]:
        return [ self._get_UImage_by_key(key) for key in self._UImage_grp.keys() ]
        
    def get_all_UImage_uuids(self) -> List[bytes]:
        return [ uuid.UUID(key).bytes for key in self._UImage_grp.keys() ]
        
    def _get_UImage_by_key(self, key, check_key=True) -> Union[UImage, None]:
        data = self._group_read_bytes(self._UImage_grp, key, check_key=check_key)
        if data is None:
            return None
        uimg = UImage.from_state(pickle.loads(data))

        image_data = self._group_read_bytes(self._UImage_image_data_grp, key, check_key=check_key)
        if image_data is not None:
            uimg.assign_image (cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), flags=cv2.IMREAD_UNCHANGED))

        return uimg

    def get_UImage_by_uuid(self, uuid : bytes) -> Union[UImage, None]:
        return self._get_UImage_by_key(uuid.hex())

    def delete_UImage_by_uuid(self, uuid : bytes):
        key = uuid.hex()
        if key in self._UImage_grp:
            del self._UImage_grp[key]
        if key in self._UImage_image_data_grp:
            del self._UImage_image_data_grp[key]

    def iter_UImage(self, include_key=False) -> Generator[UImage, None, None]:
        """
        returns Generator of UImage
        """
        for key in self._UImage_grp.keys():
            uimg = self._get_UImage_by_key(key, check_key=False)
            yield (uimg, key) if include_key else uimg

    def delete_all_UImage(self):
        """
        deletes all UImage from DB
        """
        for key in self._UImage_grp.keys():
            del self._UImage_grp[key]
        for key in self._UImage_image_data_grp.keys():
            del self._UImage_image_data_grp[key]

    ###################
    ### UPerson
    ###################

    def add_UPerson(self, uperson_or_list : UPerson, update_existing=True):
        """
        add or update UPerson in DB
        """
        if not isinstance(uperson_or_list, Iterable):
            uperson_or_list : List[UPerson] = [uperson_or_list]

        for uperson in uperson_or_list:
            self._group_write_bytes(self._UPerson_grp, uperson.get_uuid().hex(), pickle.dumps(uperson.dump_state()), update_existing=update_existing )

    def get_UPerson_count(self) -> int:
        return len(self._UPerson_grp.keys())

    def get_all_UPerson(self) -> List[UPerson]:
        return [ UPerson.from_state(pickle.loads(self._group_read_bytes(self._UPerson_grp, key, check_key=False))) for key in self._UPerson_grp.keys() ]
    
    def get_all_UPerson_uuids(self) -> List[bytes]:
        return [ uuid.UUID(key).bytes for key in self._UPerson_grp.keys() ]
    
    def get_UPerson_by_uuid(self, uuid : bytes) -> Union[UPerson, None]:
        data = self._group_read_bytes(self._UPerson_grp, uuid.hex())
        if data is None:
            return None
        return UPerson.from_state(pickle.loads(data))

    def delete_UPerson_by_uuid(self, uuid : bytes) -> bool:
        key = uuid.hex()
        if key in self._UPerson_grp:
            del self._UPerson_grp[key]
            return True
        return False

    def iter_UPerson(self) -> Generator[UPerson, None, None]:
        """
        returns Generator of UPerson
        """
        for key in self._UPerson_grp.keys():
            yield UPerson.from_state(pickle.loads(self._group_read_bytes(self._UPerson_grp, key, check_key=False)))

    def delete_all_UPerson(self):
        """
        deletes all UPerson from DB
        """
        for key in self._UPerson_grp.keys():
            del self._UPerson_grp[key]
