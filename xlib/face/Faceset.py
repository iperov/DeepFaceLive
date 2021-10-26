import pickle
import sqlite3
from pathlib import Path
from typing import Generator, List, Union, Iterable

import cv2
import numpy as np

from .FMask import FMask
from .UFaceMark import UFaceMark
from .UImage import UImage
from .UPerson import UPerson

class Faceset:

    def __init__(self, path = None):
        """
        Faceset is a class to store and manage face related data.

        arguments:

            path       path to faceset .dfs file

        Can be pickled.
        """
        self._path = path = Path(path)
        if path.suffix != '.dfs':
            raise ValueError('Path must be a .dfs file')

        self._conn = conn = sqlite3.connect(path, isolation_level=None)
        self._cur = cur = conn.cursor()

        cur = self._get_cursor()
        cur.execute('BEGIN IMMEDIATE')
        if not self._is_table_exists('FacesetInfo'):
            self.recreate(shrink=False, _transaction=False)
            cur.execute('COMMIT')
            self.shrink()
        else:
            cur.execute('END')

    def __del__(self):
        self.close()

    def __getstate__(self):
        return {'_path' : self._path}

    def __setstate__(self, d):
        self.__init__( d['_path'] )

    def __repr__(self): return self.__str__()
    def __str__(self):
        return f"Faceset. UImage:{self.get_UImage_count()} UFaceMark:{self.get_UFaceMark_count()} UPerson:{self.get_UPerson_count()}"

    def _is_table_exists(self, name):
        return self._cur.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?", [name]).fetchone()[0] != 0

    def _get_cursor(self) -> sqlite3.Cursor: return self._cur

    def close(self):
        if self._cur is not None:
            self._cur.close()
            self._cur = None

        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def shrink(self):
        self._cur.execute('VACUUM')

    def recreate(self, shrink=True, _transaction=True):
        """
        delete all data and recreate Faceset structure.
        """
        cur = self._get_cursor()

        if _transaction:
            cur.execute('BEGIN IMMEDIATE')

        for table_name, in cur.execute("SELECT name from sqlite_master where type = 'table';").fetchall():
            cur.execute(f'DROP TABLE {table_name}')

        (cur.execute('CREATE TABLE FacesetInfo (version INT)')
            .execute('INSERT INTO  FacesetInfo VALUES (1)')

            .execute('CREATE TABLE UImage (uuid BLOB, name TEXT, format TEXT, data BLOB)')
            .execute('CREATE TABLE UPerson (uuid BLOB, data BLOB)')
            .execute('CREATE TABLE UFaceMark (uuid BLOB, UImage_uuid BLOB, UPerson_uuid BLOB, data BLOB)')
            )

        if _transaction:
            cur.execute('COMMIT')

        if shrink:
            self.shrink()

    ###################
    ### UFaceMark
    ###################
    def _UFaceMark_from_db_row(self, db_row) -> UFaceMark:
        uuid, UImage_uuid, UPerson_uuid, data = db_row

        ufm = UFaceMark()
        ufm.restore_state(pickle.loads(data))
        return ufm

    def add_UFaceMark(self, ufacemark_or_list : UFaceMark):
        """
        add or update UFaceMark in DB
        """
        if not isinstance(ufacemark_or_list, Iterable):
            ufacemark_or_list : List[UFaceMark] = [ufacemark_or_list]

        cur = self._cur
        cur.execute('BEGIN IMMEDIATE')
        for ufm in ufacemark_or_list:
            uuid = ufm.get_uuid()
            UImage_uuid = ufm.get_UImage_uuid()
            UPerson_uuid = ufm.get_UPerson_uuid()

            data = pickle.dumps(ufm.dump_state())

            if cur.execute('SELECT COUNT(*) from UFaceMark where uuid=?', [uuid] ).fetchone()[0] != 0:
                cur.execute('UPDATE UFaceMark SET UImage_uuid=?, UPerson_uuid=?, data=? WHERE uuid=?',
                            [UImage_uuid, UPerson_uuid, data, uuid])
            else:
                cur.execute('INSERT INTO UFaceMark VALUES (?, ?, ?, ?)', [uuid, UImage_uuid, UPerson_uuid, data])
        cur.execute('COMMIT')

    def get_UFaceMark_count(self) -> int:
        return self._cur.execute('SELECT COUNT(*) FROM UFaceMark').fetchone()[0]

    def get_all_UFaceMark(self) -> List[UFaceMark]:
        return [ self._UFaceMark_from_db_row(db_row) for db_row in self._cur.execute('SELECT * FROM UFaceMark').fetchall() ]

    def get_UFaceMark_by_uuid(self, uuid : bytes) -> Union[UFaceMark, None]:
        c = self._cur.execute('SELECT * FROM UFaceMark WHERE uuid=?', [uuid])
        db_row = c.fetchone()
        if db_row is None:
            return None

        return self._UFaceMark_from_db_row(db_row)

    def iter_UFaceMark(self) -> Generator[UFaceMark, None, None]:
        """
        returns Generator of UFaceMark
        """
        for db_row in self._cur.execute('SELECT * FROM UFaceMark').fetchall():
            yield self._UFaceMark_from_db_row(db_row)

    def delete_all_UFaceMark(self):
        """
        deletes all UFaceMark from DB
        """
        (self._cur.execute('BEGIN IMMEDIATE')
                  .execute('DELETE FROM UFaceMark')
                  .execute('COMMIT') )
    ###################
    ### UPerson
    ###################
    def _UPerson_from_db_row(self, db_row) -> UPerson:
        uuid, data = db_row
        up = UPerson()
        up.restore_state(pickle.loads(data))
        return up

    def add_UPerson(self, uperson_or_list : UPerson):
        """
        add or update UPerson in DB
        """
        if not isinstance(uperson_or_list, Iterable):
            uperson_or_list : List[UPerson] = [uperson_or_list]

        cur = self._cur
        cur.execute('BEGIN IMMEDIATE')
        for uperson in uperson_or_list:
            uuid = uperson.get_uuid()

            data = pickle.dumps(uperson.dump_state())

            if cur.execute('SELECT COUNT(*) from UPerson where uuid=?', [uuid]).fetchone()[0] != 0:
                cur.execute('UPDATE UPerson SET data=? WHERE uuid=?', [data])
            else:
                cur.execute('INSERT INTO UPerson VALUES (?, ?)', [uuid, data])
        cur.execute('COMMIT')

    def get_UPerson_count(self) -> int:
        return self._cur.execute('SELECT COUNT(*) FROM UPerson').fetchone()[0]

    def get_all_UPerson(self) -> List[UPerson]:
        return [ self._UPerson_from_db_row(db_row) for db_row in self._cur.execute('SELECT * FROM UPerson').fetchall() ]

    def iter_UPerson(self) -> Generator[UPerson, None, None]:
        """
        iterator of all UPerson's
        """
        for db_row in self._cur.execute('SELECT * FROM UPerson').fetchall():
            yield self._UPerson_from_db_row(db_row)

    def delete_all_UPerson(self):
        """
        deletes all UPerson from DB
        """
        (self._cur.execute('BEGIN IMMEDIATE')
                  .execute('DELETE FROM UPerson')
                  .execute('COMMIT') )

    ###################
    ### UImage
    ###################
    def _UImage_from_db_row(self, db_row) -> UImage:
        uuid, name, format, data_bytes = db_row
        img = cv2.imdecode(np.frombuffer(data_bytes, dtype=np.uint8), flags=cv2.IMREAD_UNCHANGED)

        uimg = UImage()
        uimg.set_uuid(uuid)
        uimg.set_name(name)
        uimg.assign_image(img)
        return uimg

    def add_UImage(self, uimage_or_list : UImage, format : str = 'webp', quality : int = 100):
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
            uimage_or_list = [uimage_or_list]

        uimage_datas = []
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
            uimage_datas.append(data_bytes.data)

        cur = self._cur
        cur.execute('BEGIN IMMEDIATE')
        for uimage, data in zip(uimage_or_list, uimage_datas):
            uuid = uimage.get_uuid()
            if cur.execute('SELECT COUNT(*) from UImage where uuid=?', [uuid] ).fetchone()[0] != 0:
                cur.execute('UPDATE UImage SET name=?, format=?, data=? WHERE uuid=?', [uimage.get_name(), format, data, uuid])
            else:
                cur.execute('INSERT INTO UImage VALUES (?, ?, ?, ?)', [uuid, uimage.get_name(), format, data])
        cur.execute('COMMIT')

    def get_UImage_count(self) -> int: return self._cur.execute('SELECT COUNT(*) FROM UImage').fetchone()[0]
    def get_UImage_by_uuid(self, uuid : Union[bytes, None]) -> Union[UImage, None]:
        """
        """
        if uuid is None:
            return None

        db_row = self._cur.execute('SELECT * FROM UImage where uuid=?', [uuid]).fetchone()
        if db_row is None:
            return None
        return self._UImage_from_db_row(db_row)

    def iter_UImage(self) -> Generator[UImage, None, None]:
        """
        iterator of all UImage's
        """
        for db_row in self._cur.execute('SELECT * FROM UImage').fetchall():
            yield self._UImage_from_db_row(db_row)

    def delete_all_UImage(self):
        """
        deletes all UImage from DB
        """
        (self._cur.execute('BEGIN IMMEDIATE')
                  .execute('DELETE FROM UImage')
                  .execute('COMMIT') )
