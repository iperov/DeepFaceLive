import multiprocessing
from operator import mul
import uuid
from typing import Union
from ..io import FormattedMemoryViewIO
from .MPSharedMemory import MPSharedMemory


class MPSPSCMRRingData:
    """
    Multiprocess lockless Single Producer, Single Consumer, Multi Reader Ring Data.

    Producer knows how many data is read by Consumer (by accessing read_id)

    Side readers can read last data without locks.

    The data returned is either valid or None.
    """

    def __init__(self, table_size, heap_size_mb, multi_producer : bool = False):
        self._table_size = table_size
        self._heap_size = heap_size = heap_size_mb*1024*1024
        self._write_lock = multiprocessing.Lock() if multi_producer else None
        self._event = multiprocessing.Event()

        self._sizeof_uuid = 16

        table_item_size = self._table_item_size = 8+8+self._sizeof_uuid
        self._table_offset = 8+8
        self._heap_offset = self._table_offset + table_size*table_item_size

        self._shared_mem = MPSharedMemory(8+8+table_size*table_item_size + heap_size)
        self._initialize_mvs()

        self._mv_ids[0] = 0 # write_id
        self._mv_ids[1] = 0 # read_id

        # Initialize first block at 0 index
        wid = 0
        wid_uuid = uuid.uuid4().bytes
        wid_heap_offset = 0
        wid_data_size = 0

        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())
        fmv.seek(self._table_offset + (wid % self._table_size)*self._table_item_size)
        fmv.write_fmt('QQ', wid_heap_offset, wid_data_size), fmv.write(wid_uuid)


    def _initialize_mvs(self):
        mv = self._shared_mem.get_mv()
        self._mv_ids = mv.cast('Q')[0:2]

    def __getstate__(self):
        d = self.__dict__.copy()
        d.pop('_mv_ids')
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self._initialize_mvs()

    def get_write_id(self) -> int: return self._mv_ids[0]
    def get_read_id(self) -> int: return self._mv_ids[1]


    def write(self, data : Union[bytes, bytearray]):
        """
        write data incrementing write_id
        """
        heap_size = self._heap_size

        if not isinstance(data, (bytes, bytearray)):
            raise ValueError('data must be an instance of bytes or bytearray')
        data_size = len(data)

        if data_size == 0:
            raise ValueError('data_size must be > 0')

        data_size_in_heap = data_size+self._sizeof_uuid
        data_size_in_heap = ( data_size_in_heap + (-data_size_in_heap & 7) )
        if data_size_in_heap > heap_size:
            raise Exception('data_size more than heap_size')

        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())
        wid_uuid = uuid.uuid4().bytes

        if self._write_lock is not None:
            self._write_lock.acquire()

        wid = self._mv_ids[0]

        # Read table record of wid
        fmv.seek(self._table_offset + (wid % self._table_size)*self._table_item_size)
        (wid_heap_offset, wid_data_size), _ = fmv.read_fmt('QQ'), fmv.read(self._sizeof_uuid)

        # Calc aligned next offset
        wid_heap_offset += self._sizeof_uuid + wid_data_size
        wid_heap_offset = ( wid_heap_offset + (-wid_heap_offset & 7) )

        # Check if next offset with data size fit remain heap space
        if wid_heap_offset+data_size_in_heap >= heap_size:
            wid_heap_offset = 0

        # Write the data into heap
        fmv.seek(self._heap_offset + wid_heap_offset)
        fmv.write(wid_uuid)
        fmv.write(data)

        # Write new table record
        wid += 1
        fmv.seek(self._table_offset + (wid % self._table_size)*self._table_item_size)
        fmv.write_fmt('QQ', wid_heap_offset, data_size), fmv.write(wid_uuid)

        # Set new write_id
        self._mv_ids[0] = wid

        if self._write_lock is not None:
            self._write_lock.release()
            
        self._event.set()

    
        
    def get_by_id(self, id) -> Union[bytearray, None]:
        """
        get data by id
        """
        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())
        sizeof_uuid = self._sizeof_uuid

        # Read table record
        fmv.seek(self._table_offset + (id % self._table_size)*self._table_item_size)
        (rid_heap_offset, rid_data_size), rid_uuid = fmv.read_fmt('QQ'), fmv.read(sizeof_uuid)

        if rid_data_size == 0:
            return None

        # Seek to the data in the heap
        fmv.seek(self._heap_offset + rid_heap_offset)

        # Check data validness
        if fmv.read(sizeof_uuid) != rid_uuid:
            return None

        # read the data
        result = fmv.read(rid_data_size)

        # Check data validness again
        fmv.seek(self._heap_offset + rid_heap_offset)
        if fmv.read(sizeof_uuid) != rid_uuid:
            return None

        return result

    def read(self, timeout=0, update_rid=True) -> Union[bytearray, None]:
        """
        read data incrementing read_id
        """
        if self._mv_ids[0] == self._mv_ids[1]:
            if timeout == 0:
                return None
            if not self._event.wait(timeout):
                return None
            self._event.clear()
                
        wid, rid = self._mv_ids[0], self._mv_ids[1]
        
        result = None
        while rid < wid:
            rid = rid+1
            result = self.get_by_id(rid)
            if result is not None:
                break

        if update_rid:
            self._mv_ids[1] = rid
        return result
        
    # def wait_for_read(self, timeout : float) -> bool:
    #     """
    #     returns True if ready to .read()
    #     """
    #     result = self._event.wait(timeout)
    #     if result:
    #         self._event.clear()
    #     return result