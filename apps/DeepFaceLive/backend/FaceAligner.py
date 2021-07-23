import time

import numpy as np
from xlib import os as lib_os
from xlib.facemeta import FaceAlign, FaceULandmarks
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class FaceAligner(BackendHost):
    def __init__(self, weak_heap :  BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, backend_db : BackendDB = None):
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceAlignerWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out])

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

class FaceAlignerWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.pending_bcd = None
        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()
        cs.face_coverage.call_on_number(self.on_cs_face_coverage)
        cs.resolution.call_on_number(self.on_cs_resolution)
        cs.exclude_moving_parts.call_on_flag(self.on_cs_exclude_moving_parts)

        cs.face_coverage.enable()
        cs.face_coverage.set_config(lib_csw.Number.Config(min=0.1, max=4.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.face_coverage.set_number(state.face_coverage if state.face_coverage is not None else 2.2)

        cs.resolution.enable()
        cs.resolution.set_config(lib_csw.Number.Config(min=16, max=1024, step=16, decimals=0, allow_instant_update=True))
        cs.resolution.set_number(state.resolution if state.resolution is not None else 224)

        cs.exclude_moving_parts.enable()

        cs.exclude_moving_parts.set_flag(state.exclude_moving_parts if state.exclude_moving_parts is not None else True)

    def on_cs_face_coverage(self, face_coverage):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_coverage.get_config()
        face_coverage = state.face_coverage = np.clip(face_coverage, cfg.min, cfg.max)
        cs.face_coverage.set_number(face_coverage)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_resolution(self, resolution):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.resolution.get_config()
        resolution = state.resolution = int(np.clip( (resolution//16)*16, cfg.min, cfg.max))
        cs.resolution.set_number(resolution)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_exclude_moving_parts(self, exclude_moving_parts):
        state, cs = self.get_state(), self.get_control_sheet()
        state.exclude_moving_parts = exclude_moving_parts
        self.save_state()
        self.reemit_frame_signal.send()

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                frame_name = bcd.get_frame_name()
                frame_image = bcd.get_image(frame_name)

                if all_is_not_None(state.face_coverage, state.resolution, frame_name, frame_image):
                    for face_id,face_mark in enumerate( bcd.get_face_mark_list() ):
                        face_ulmrks = face_mark.get_face_ulandmarks_by_type(FaceULandmarks.Type.LANDMARKS_2D_468)
                        if face_ulmrks is None:
                            face_ulmrks = face_mark.get_face_ulandmarks_by_type(FaceULandmarks.Type.LANDMARKS_2D_68)

                        if face_ulmrks is not None:
                            face_image, uni_mat = face_ulmrks.cut(frame_image, state.face_coverage, state.resolution, exclude_moving_parts=state.exclude_moving_parts)

                            face_align_image_name = f'{frame_name}_{face_id}_aligned'

                            face_align = FaceAlign()
                            face_align.set_image_name(face_align_image_name)
                            face_align.set_coverage(state.face_coverage)
                            face_align.set_source_face_ulandmarks_type(face_ulmrks.get_type())
                            face_align.set_source_to_aligned_uni_mat(uni_mat)

                            for face_ulmrks in face_mark.get_face_ulandmarks_list():
                                face_align.add_face_ulandmarks( face_ulmrks.transform(uni_mat) )
                            face_mark.set_face_align(face_align)

                            bcd.set_image(face_align_image_name, face_image)

                self.stop_profile_timing()
                self.pending_bcd = bcd

        if self.pending_bcd is not None:
            if self.bc_out.is_full_read(1):
                self.bc_out.write(self.pending_bcd)
                self.pending_bcd = None
            else:
                time.sleep(0.001)


class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.face_coverage = lib_csw.Number.Client()
            self.resolution = lib_csw.Number.Client()
            self.exclude_moving_parts = lib_csw.Flag.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.face_coverage = lib_csw.Number.Host()
            self.resolution = lib_csw.Number.Host()
            self.exclude_moving_parts = lib_csw.Flag.Host()

class WorkerState(BackendWorkerState):
    face_coverage : float = None
    resolution    : int = None
    exclude_moving_parts : bool = None
