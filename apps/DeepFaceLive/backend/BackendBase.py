import multiprocessing
import pickle
from typing import List, Union, Tuple

import numpy as np
from xlib import mp as lib_mp
from xlib import time as lib_time
from xlib.mp import csw as lib_csw
from xlib.python.EventListener import EventListener

from xlib.face import FRect, FLandmarks2D, FPose

class BackendFaceSwapInfo:
    def __init__(self):
        self.image_name = None
        self.face_urect : FRect = None
        self.face_pose : FPose = None
        self.face_ulmrks : FLandmarks2D = None

        self.face_resolution : int = None
        self.face_align_image_name : str = None
        self.face_align_mask_name : str = None
        self.face_align_lmrks_mask_name : str = None
        self.face_anim_image_name : str = None
        self.face_swap_image_name : str = None
        self.face_swap_mask_name : str = None

        self.image_to_align_uni_mat = None
        self.face_align_ulmrks : FLandmarks2D = None

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__init__()
        self.__dict__.update(d)

class BackendConnectionData:
    """
    data class for BackendConnection

    Should not contain large buffers.
    Large buffers are stored via MPWeakHeap
    """

    def __init__(self, uid ):
        super().__init__()
        self._weak_heap = None
        self._weak_heap_refs = {}
        self._weak_heap_image_infos = {}

        self._uid = uid
        self._is_frame_reemitted = None

        self._frame_image_name = None
        self._frame_count = None
        self._frame_num = None
        self._frame_fps = None
        self._frame_timestamp = None
        self._merged_image_name = None

        self._face_swap_info_list = []

    def __getstate__(self, ):
        d = self.__dict__.copy()
        d['_weak_heap'] = None
        return d

    def assign_weak_heap(self, weak_heap : lib_mp.MPWeakHeap):
        self._weak_heap = weak_heap

    def set_file(self, key, data : Union[bytes, bytearray, memoryview]):
        self._weak_heap_refs[key] = self._weak_heap.add_data(data)

    def get_file(self, key) -> Union[bytes, None]:
        ref = self._weak_heap_refs.get(key, None)
        if ref is not None:
            return self._weak_heap.get_data(ref)
        return None

    def set_image(self, key, image : np.ndarray):
        """
        store image to weak heap

            key

            image  np.ndarray
        """
        self.set_file(key, image.data)
        self._weak_heap_image_infos[key] = (image.shape, image.dtype)

    def get_image_shape_dtype(self, key) -> Union[None, Tuple[List, np.dtype]]:
        """
        returns (image shape, dtype) or (None, None) if file does not exist
        """
        if key is None:
            return (None, None)
        image_info = self._weak_heap_image_infos.get(key, None)
        if image_info is not None:
            shape, dtype = image_info
            return shape, dtype
        return (None, None)

    def get_image(self, key) -> Union[np.ndarray, None]:
        if key is None:
            return None
        image_info = self._weak_heap_image_infos.get(key, None)
        buffer = self.get_file(key)

        if image_info is not None and buffer is not None:
            shape, dtype = image_info
            return np.ndarray(shape, dtype=dtype, buffer=buffer)
        return None

    def get_uid(self) -> int: return self._uid

    def get_is_frame_reemitted(self) -> Union[bool, None]: return self._is_frame_reemitted
    def set_is_frame_reemitted(self, is_frame_reemitted : bool): self._is_frame_reemitted = is_frame_reemitted
    def get_frame_count(self) -> Union[int, None]: return self._frame_count
    def set_frame_count(self, frame_count : int): self._frame_count = frame_count
    def get_frame_num(self) -> Union[int, None]: return self._frame_num
    def set_frame_num(self, frame_num : int): self._frame_num = frame_num
    def get_frame_fps(self) -> Union[float, None]: return self._frame_fps
    def set_frame_fps(self, frame_fps  : float): self._frame_fps = frame_fps
    def get_frame_timestamp(self) -> Union[float, None]: return self._frame_timestamp
    def set_frame_timestamp(self, frame_timestamp : float): self._frame_timestamp = frame_timestamp

    def get_frame_image_name(self) -> Union[str, None]: return self._frame_image_name
    def set_frame_image_name(self, frame_image_name : str): self._frame_image_name = frame_image_name
    def get_merged_image_name(self) -> Union[str, None]: return self._merged_image_name
    def set_merged_image_name(self, merged_frame_name : str): self._merged_image_name = merged_frame_name

    def get_face_swap_info_list(self) -> List[BackendFaceSwapInfo]: return self._face_swap_info_list
    def add_face_swap_info(self, fsi : BackendFaceSwapInfo):
        if not isinstance(fsi, BackendFaceSwapInfo):
            raise ValueError(f'fsi must be an instance of BackendFaceSwapInfo')
        self._face_swap_info_list.append(fsi)



class BackendConnection:
    def __init__(self, multi_producer=False):
        self._rd = lib_mp.MPSPSCMRRingData(table_size=8192, heap_size_mb=8, multi_producer=multi_producer)

    def write(self, bcd : BackendConnectionData):
        self._rd.write( pickle.dumps(bcd) )

    def read(self, timeout : float = 0) -> Union[BackendConnectionData, None]:
        b = self._rd.read(timeout=timeout)
        if b is not None:
            return pickle.loads(b)
        return None

    def get_write_id(self) -> int:
        return self._rd.get_write_id()

    def get_by_id(self, id) -> Union[BackendConnectionData, None]:
        b = self._rd.get_by_id(id)
        if b is not None:
            return pickle.loads(b)
        return None

    def wait_for_read(self, timeout : float) -> bool:
        """
        returns True if ready to .read()
        """
        return self._rd.wait_for_read(timeout)

    def is_full_read(self, buffer_size=0) -> bool:
        """
        if fully readed by receiver side minus buffer_size
        """
        return self._rd.get_read_id() >= (self._rd.get_write_id() - buffer_size)


class BackendSignal:
    def __init__(self):
        self._ev = multiprocessing.Event()

    def send(self):
        self._ev.set()

    def recv(self):
        is_set = self._ev.is_set()
        if is_set:
            self._ev.clear()
        return is_set

class BackendWeakHeap(lib_mp.MPWeakHeap):
    ...

class BackendDB(lib_csw.DB):
    ...

class BackendWorkerState(lib_csw.WorkerState):
    ...

class BackendHost(lib_csw.Host):
    def __init__(self, backend_db : BackendDB = None,
                       sheet_cls = None,
                       worker_cls = None,
                       worker_state_cls : BackendWorkerState = None,
                       worker_start_args = None,
                       worker_start_kwargs = None):

        super().__init__(db=backend_db,
                         sheet_cls = sheet_cls,
                         worker_cls = worker_cls,
                         worker_state_cls = worker_state_cls,
                         worker_start_args = worker_start_args,
                         worker_start_kwargs = worker_start_kwargs)

        self._profile_timing_evl = EventListener()
        self.call_on_msg('_profile_timing', self._on_profile_timing_msg)

    def _on_profile_timing_msg(self, timing : float):
        self._profile_timing_evl.call(timing)

    def call_on_profile_timing(self, func_or_list):
        self._profile_timing_evl.add(func_or_list)

class BackendWorker(lib_csw.Worker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._profile_timing_measurer = lib_time.AverageMeasurer(samples=120)

    def start_profile_timing(self):
        self._profile_timing_measurer.start()

    def stop_profile_timing(self):
        self.send_msg('_profile_timing', self._profile_timing_measurer.stop() )

