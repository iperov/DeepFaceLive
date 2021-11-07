import multiprocessing
import uuid
from typing import Union

from ..io import FormattedMemoryViewIO
from .MPSharedMemory import MPSharedMemory


class MPWeakHeap:
    """
    Multiprocess weak heap.


    heap structure

    |ring_head_block_offset block block block ...|

    block structure:
        ---
        (8) block_size

        (8) data_size

        (16) UUID sig

        ...data...

    """
    class DataRef:
        def __init__(self, block_offset, uuid : bytes):
            self._block_offset = block_offset
            self._uuid = uuid

    def __init__(self, size_mb : int):


        self._heap_size = size_mb * 1024 * 1024 # should be 16 byte aligned
        self._shared_mem = MPSharedMemory(self._heap_size)
        self._lock = multiprocessing.Lock()

        # Initialize heap structure
        self._ring_head_block_offset = 0
        self._first_block_offset = 8
        self._block_header_size = 8+8+16
        self._block_data_start_offset = 8+8+16

        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())
        fmv.seek(self._ring_head_block_offset), fmv.write_fmt('q', self._first_block_offset)

        # Entire block
        fmv.seek(self._first_block_offset)
        fmv.write_fmt('qq', self._heap_size-self._first_block_offset, 0), fmv.write(uuid.uuid4().bytes)


    def add_data(self, data : Union[bytes, bytearray, memoryview] ) -> 'MPWeakHeap.DataRef':
        """
        add the data to the head of ring

            data

        """
        heap_size = self._heap_size
        block_header_size = self._block_header_size

        if isinstance(data, memoryview):
            data = data.cast('B')
            if not data.contiguous:
                raise ValueError('data as memoryview should be contiguous')
            data_size = data.nbytes
        else:
            data_size = len(data)

        lock = self._lock
        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())
        lock.acquire()

        # start from ring_head_block_offset
        fmv.seek(self._ring_head_block_offset)
        cur_block_offset, = fmv.read_fmt('q')

        while True:
            fmv.seek(cur_block_offset)
            block_size, = fmv.get_fmt('q')
            block_free_size = block_size - block_header_size

            if data_size <= block_free_size:
                # the space of the block is enough for the data

                block_new_size = block_header_size + ( data_size + (-data_size & 7) )
                block_remain_size = block_size-block_new_size

                if block_remain_size >= block_header_size:
                    # the remain space of the block is enough for next block, split the block
                    next_block_offset = cur_block_offset + block_new_size
                    fmv.seek(next_block_offset), fmv.write_fmt('qq', block_remain_size, 0), fmv.write(uuid.uuid4().bytes)
                else:
                    # otherwise do not split
                    next_block_offset = cur_block_offset + block_size
                    if next_block_offset >= heap_size:
                        next_block_offset = self._first_block_offset
                    block_new_size = block_size

                # update current block structure
                uid = uuid.uuid4().bytes
                fmv.seek(cur_block_offset), fmv.write_fmt('qq', block_new_size, data_size ), fmv.write(uid)

                # update ring_head_block_offset
                fmv.seek(self._ring_head_block_offset),  fmv.write_fmt('q', next_block_offset)

                lock.release()

                # write the data into the block
                fmv.seek(cur_block_offset+self._block_data_start_offset)
                fmv.write(data)

                return MPWeakHeap.DataRef(cur_block_offset, uid)
            else:
                # the space of the block is not enough for the daata
                is_first_block = cur_block_offset == self._first_block_offset
                is_last_block = (cur_block_offset+block_size) >= heap_size

                if is_last_block:
                    if is_first_block:
                        lock.release()
                        raise Exception(f'Not enough space in MPWeakHeap to allocate {data_size}')

                    # if it is last block, leave it unchanged, and continue with first block
                    cur_block_offset = self._first_block_offset
                    continue
                else:
                    # not last block, merge with next block

                    # get next block size
                    fmv.seek(cur_block_offset+block_size)
                    next_block_size, = fmv.get_fmt('q')

                    # erase data of next block
                    fmv.write_fmt('qq', 0, 0), fmv.write(uuid.uuid4().bytes)

                    # overwrite current block size with expanded block size
                    fmv.seek(cur_block_offset)
                    fmv.write_fmt('q', block_size+next_block_size)

                    # continue with the same expanded block
                    continue


    def get_data(self, data_ref : 'MPWeakHeap.DataRef') -> Union[bytearray, None]:
        """
        Get data

        if data is overwritten already, None will be returned
        """
        lock = self._lock
        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())

        # short lock to get data info
        fmv.seek(data_ref._block_offset)
        lock.acquire()
        (_, data_size), uuid = fmv.read_fmt('qq'), fmv.read(16)
        lock.release()

        # Check valid UUID
        if data_ref._uuid != uuid:
            return None

        # read the data
        result = fmv.read(data_size)

        # short lock again to validate that the reference is still valid,
        # thus we read valid data
        fmv.seek(data_ref._block_offset)
        lock.acquire()
        (_, data_size), uuid = fmv.read_fmt('qq'), fmv.read(16)
        lock.release()

        # Check valid UUID
        if data_ref._uuid != uuid:
            return None

        return result

    def summary(self) -> str:
        """
        returns a string with summary of heap
        """
        result = []


        heap_size = self._heap_size
        fmv = FormattedMemoryViewIO(self._shared_mem.get_mv())

        lock = self._lock
        lock.acquire()

        head_block_offset, = fmv.read_fmt('q')

        cur_block_offset = self._first_block_offset

        block_id = 0
        while cur_block_offset != self._heap_size:
            fmv.seek(cur_block_offset)
            (block_size, data_size), sig = fmv.read_fmt('qq'), fmv.read(16)


            s = ''
            if cur_block_offset == head_block_offset:
                s += f'[{block_id} HEAD]:'
            else:
                s += f'[{block_id}]:'

            if data_size != 0:
                s += f'block_size: {block_size} data_size:{data_size}'
            else:
                s += f'block_size: {block_size} empty'
            result.append(s)
            block_id += 1

            cur_block_offset += block_size
        lock.release()

        return '\n'.join(result)
