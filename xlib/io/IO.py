import io
import pickle
import struct
from pathlib import Path
from typing import Union


class FormattedIOBase:
    """
    base class for formatting IO-like objects

    methods should be implemented:

        write
        read
        seek
        tell
    """
    def get_file_size(self):
        c = self.tell()
        result = self.seek(0,2)
        self.seek(c)
        return result

    def fill(self, byte, size : int):
        """fills a byte with length of size"""
        c_size = 16384
        n_count = size // c_size
        m_count = size % c_size
        f = bytes([byte]) * c_size

        if n_count >= 1:
            for _ in range(n_count):
                self.write(f)
        if m_count > 0:
            self.write(f[:m_count])
        return size

    def write_bytes(self, b_bytes):
        """writes compact bytes() object"""
        self.write_fmt('Q', len(b_bytes))
        self.write(b_bytes)

    def read_bytes(self):
        """reads bytes() object"""
        return self.read( self.read_fmt('Q')[0] )

    def write_utf8(self, s):
        """write compact string as utf8. Length must be not larger than 4Gb"""
        b = s.encode('utf-8')
        self.write_fmt('I', len(b))
        self.write(b)

    def read_utf8(self):
        """read string from utf8"""
        return self.read(self.read_fmt('I')[0]).decode('utf-8')

    def calc_fmt(self, fmt):
        """calc size for _fmt functions"""
        return struct.calcsize(fmt)

    def write_fmt_at(self, offset, fmt, *args):
        """
        write_fmt at offset and return cursor where it was
        """
        c = self.tell()
        self.seek(offset,0)
        n = self.write_fmt(fmt, *args)
        self.seek(c)
        return n

    def write_fmt(self, fmt, *args):
        """
        write compact data using struct.pack
        """
        b = struct.pack(fmt, *args)
        n_written = self.write(b)
        if n_written != len(b):
            raise IOError('Not enough room for write_fmt')
        return n_written

    def get_fmt(self, fmt):
        """read using struct.unpack without incrementing a cursor"""
        c = self.tell()
        result = self.read_fmt(fmt)
        self.seek(c)
        return result

    def read_fmt(self, fmt):
        """
        read using struct.unpack
        """
        size = struct.calcsize(fmt)

        b = self.read(size)
        if size != len(b):
            raise IOError('Not enough room for read_fmt')

        return struct.unpack (fmt, b)

    def read_backward_fmt(self, fmt):
        """
        read using struct.unpack in backward direction
        """
        size = struct.calcsize(fmt)

        cursor = self.tell()
        new_cursor = self.seek(-size,1)

        if size != cursor-new_cursor:
            raise IOError('Not enough room for read_backward_fmt')

        b = self.read(size)
        self.seek(-size,1)

        return struct.unpack (fmt, b)

    def write_pickled(self, obj):
        """
        write pickled obj
        """
        c = self.tell()
        self.write_fmt('Q', 0)

        pickle.dump(obj, self, 4)
        size = self.tell() - c

        self.write_fmt_at(c, 'Q', size)
        return size

    def read_pickled(self, suppress_error=True):
        """
        read pickled object

            suppress_error(True)    ignore unpickling errors
                                    the stream will not be corrupted
        """
        c = self.tell()
        size, = self.read_fmt('Q')

        if suppress_error:
            try:
                obj = pickle.load(self)
            except:
                obj = None
        else:
            obj = pickle.load(self)

        self.seek(c+size)

        return obj


class FormattedFileIO(io.FileIO, FormattedIOBase):
    """
    FileIO to use with formatting methods
    """
    def __init__(self, file, mode: str, closefd: bool = True, opener = None):
        filepath = Path(file)
        plus = '+' if '+' in mode else ''
        if 'a' in mode:
            if filepath.exists():
                mode = 'r' + plus
            else:
                mode = 'w' + plus

        io.FileIO.__init__(self, file, mode, closefd=closefd, opener=opener)



    def seek(self, offset, whence=0):
        """
        seek to offset

         whence     0(default) : from begin   , offset >= 0
                    1          : from current , offset any
                    2          : from end     , offset any

        returns cursor after seek
        """
        # reimplement method to allow to expand with zeros

        offset_cur = self.tell()
        offset_max = io.FileIO.seek(self, 0,2)

        if whence == 1:
            offset += offset_cur
        elif whence == 2:
            offset += offset_max

        expand = offset - offset_max
        if expand > 0:
            # new offset will be more than file size
            # expand with zero bytes
            self.fill(0x00, expand)

        return io.FileIO.seek(self, offset)

    def readinto (self, bytes_like : Union[bytearray, memoryview], size : int = 0):
        """read size amount of bytes into mutable bytes_like"""
        if size == 0:
            return io.FileIO.readinto(self, bytes_like)
        else:
            return io.FileIO.readinto(self, memoryview(bytes_like).cast('B')[:size] )

    def write(self, b: Union[bytes, bytearray, memoryview]):
        b_len = len(b)
        acc = 0
        n_count = b_len // 16384
        m_count = b_len % 16384
        if n_count > 0:
            for i in range(n_count):
                acc += io.FileIO.write(self, b[i*16384:(i+1)*16384])
        if m_count > 0:
            acc += io.FileIO.write(self, b[n_count*16384:])
        return acc



class FormattedMemoryViewIO(io.RawIOBase, FormattedIOBase):
    """file-IO-like to memoryview"""
    def __init__(self, mv : memoryview):
        super().__init__()
        self._mv = mv
        self._mv_size = self._c_max = mv.nbytes
        self._c = 0

    def seek(self, cursor, whence=0):
        """
        seek to offset

         whence     0(default) : from begin   , offset >= 0
                    1          : from current , offset any
                    2          : from end     , offset any

        returns cursor after seek
        """
        # memoryview is not expandable, thus just clip the cursor
        if whence == 0:
            self._c = min( max(cursor,0), self._mv_size)
            self._c_max = max(self._c, self._c_max)
        elif whence == 1:
            self._c = min( max(self._c + cursor, 0), self._mv_size)
            self._c_max = max(self._c, self._c_max)
        elif whence == 2:
            self._c = min( max(self._c_max + cursor, 0), self._mv_size)
            self._c_max = max(self._c, self._c_max)
        else:
            raise ValueError('whence != 0,1,2')

        return self._c

    def tell(self):
        """returns current cursor offset"""
        return self._c

    def truncate(self, size=None):
        """truncate to the current cursor"""
        if size is not None:
            self._c_max = min(size, self._c_max)
        else:
            self._c_max = self._c
        return self._c_max


    def write(self, b : Union[bytes, bytearray, memoryview], size=0):
        if isinstance(b, memoryview):
            b = b.cast('B')
            size = b.nbytes
        else:
            size = len(b)

        size = min(size, self._mv_size - self._c)

        self._mv[self._c:self._c+size] = b[:size]
        self._c += size
        return size

    def read_memoryview(self, size) -> memoryview:
        size = min(size, self._c_max - self._c)
        result = self._mv[self._c:self._c+size]
        self._c += size
        return result

    def read(self, size) -> bytearray:
        """
        read bytearray of size
        """
        size = min(size, self._c_max - self._c)

        result = bytearray(size)

        memoryview(result)[:] = self._mv[self._c:self._c+size]

        self._c += size
        return result

    def readinto (self, bytes_like_or_io : Union[bytearray, memoryview, io.IOBase], size):
        """read size amount of bytes into mutable bytes_like or io"""
        if isinstance(bytes_like_or_io, io.IOBase):
            bytes_like_or_io.write( self._mv[self._c:self._c+size] )
        else:
            memoryview(bytes_like_or_io).cast('B')[:size] = self._mv[self._c:self._c+size]
        self._c += size
