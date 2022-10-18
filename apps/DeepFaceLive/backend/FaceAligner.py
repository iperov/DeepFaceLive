import time
from enum import IntEnum

import numpy as np
from xlib import os as lib_os
from xlib.face import FRect
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class AlignMode(IntEnum):
    FROM_RECT = 0
    FROM_POINTS = 1
    FROM_STATIC_RECT = 2

AlignModeNames = ['@FaceAligner.AlignMode.FROM_RECT',
                  '@FaceAligner.AlignMode.FROM_POINTS',
                  '@FaceAligner.AlignMode.FROM_STATIC_RECT',
                 ]

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
        cs.align_mode.call_on_selected(self.on_cs_align_mode)
        cs.face_coverage.call_on_number(self.on_cs_face_coverage)
        cs.resolution.call_on_number(self.on_cs_resolution)
        cs.exclude_moving_parts.call_on_flag(self.on_cs_exclude_moving_parts)
        cs.head_mode.call_on_flag(self.on_cs_head_mode)
        cs.freeze_z_rotation.call_on_flag(self.on_cs_freeze_z_rotation)

        cs.x_offset.call_on_number(self.on_cs_x_offset)
        cs.y_offset.call_on_number(self.on_cs_y_offset)

        cs.align_mode.enable()
        cs.align_mode.set_choices(AlignMode, AlignModeNames)
        cs.align_mode.select(state.align_mode if state.align_mode is not None else AlignMode.FROM_POINTS)

        cs.face_coverage.enable()
        cs.face_coverage.set_config(lib_csw.Number.Config(min=0.1, max=8.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.face_coverage.set_number(state.face_coverage if state.face_coverage is not None else 2.2)

        cs.resolution.enable()
        cs.resolution.set_config(lib_csw.Number.Config(min=16, max=1024, step=16, decimals=0, allow_instant_update=True))
        cs.resolution.set_number(state.resolution if state.resolution is not None else 224)

        cs.exclude_moving_parts.enable()
        cs.exclude_moving_parts.set_flag(state.exclude_moving_parts if state.exclude_moving_parts is not None else True)

        cs.head_mode.enable()
        cs.head_mode.set_flag(state.head_mode if state.head_mode is not None else False)

        cs.freeze_z_rotation.enable()
        cs.freeze_z_rotation.set_flag(state.freeze_z_rotation if state.freeze_z_rotation is not None else False)

        cs.x_offset.enable()
        cs.x_offset.set_config(lib_csw.Number.Config(min=-10, max=10, step=0.01, decimals=2, allow_instant_update=True))
        cs.x_offset.set_number(state.x_offset if state.x_offset is not None else 0)

        cs.y_offset.enable()
        cs.y_offset.set_config(lib_csw.Number.Config(min=-10, max=10, step=0.01, decimals=2, allow_instant_update=True))
        cs.y_offset.set_number(state.y_offset if state.y_offset is not None else 0)

    def on_cs_align_mode(self, idx, align_mode):
        state, cs = self.get_state(), self.get_control_sheet()
        state.align_mode = align_mode

        self.save_state()
        self.reemit_frame_signal.send()

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

    def on_cs_head_mode(self, head_mode):
        state, cs = self.get_state(), self.get_control_sheet()
        state.head_mode = head_mode
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_freeze_z_rotation(self, freeze_z_rotation):
        state, cs = self.get_state(), self.get_control_sheet()
        state.freeze_z_rotation = freeze_z_rotation
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_x_offset(self, x_offset):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.x_offset.get_config()
        x_offset = state.x_offset = float(np.clip(x_offset, cfg.min, cfg.max))
        cs.x_offset.set_number(x_offset)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_y_offset(self, y_offset):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.y_offset.get_config()
        y_offset = state.y_offset = float(np.clip(y_offset, cfg.min, cfg.max))
        cs.y_offset.set_number(y_offset)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)

                if all_is_not_None(state.face_coverage, state.resolution, frame_image):
                    for face_id, fsi in enumerate( bcd.get_face_swap_info_list() ):
                        head_yaw = None
                        if state.head_mode or state.freeze_z_rotation:
                            if fsi.face_pose is not None:
                                head_yaw = fsi.face_pose.as_radians()[1]
                        
                        face_ulmrks = fsi.face_ulmrks
                        if face_ulmrks is not None:
                            fsi.face_resolution = state.resolution

                            H, W = frame_image.shape[:2]
                            if state.align_mode == AlignMode.FROM_RECT:
                                face_align_img, uni_mat = fsi.face_urect.cut(frame_image, coverage= state.face_coverage, output_size=state.resolution,
                                                                             x_offset=state.x_offset, y_offset=state.y_offset)

                            elif state.align_mode == AlignMode.FROM_POINTS:
                                face_align_img, uni_mat = face_ulmrks.cut(frame_image, state.face_coverage+ (1.0 if state.head_mode else 0.0), state.resolution,
                                                                          exclude_moving_parts=state.exclude_moving_parts,
                                                                          head_yaw=head_yaw,
                                                                          x_offset=state.x_offset,
                                                                          y_offset=state.y_offset-0.08 + (-0.50 if state.head_mode else 0.0),
                                                                          freeze_z_rotation=state.freeze_z_rotation)
                            elif state.align_mode == AlignMode.FROM_STATIC_RECT:
                                rect = FRect.from_ltrb([ 0.5 - (fsi.face_resolution/W)/2, 0.5 - (fsi.face_resolution/H)/2, 0.5 + (fsi.face_resolution/W)/2, 0.5 + (fsi.face_resolution/H)/2,])
                                face_align_img, uni_mat = rect.cut(frame_image, coverage= state.face_coverage, output_size=state.resolution,
                                                                             x_offset=state.x_offset, y_offset=state.y_offset)

                            fsi.face_align_image_name = f'{frame_image_name}_{face_id}_aligned'
                            fsi.image_to_align_uni_mat = uni_mat
                            fsi.face_align_ulmrks = face_ulmrks.transform(uni_mat)
                            bcd.set_image(fsi.face_align_image_name, face_align_img)

                            # Due to FaceAligner is not well loaded, we can make lmrks mask here
                            face_align_lmrks_mask_img = fsi.face_align_ulmrks.get_convexhull_mask( face_align_img.shape[:2], color=(255,), dtype=np.uint8)
                            fsi.face_align_lmrks_mask_name = f'{frame_image_name}_{face_id}_aligned_lmrks_mask'
                            bcd.set_image(fsi.face_align_lmrks_mask_name, face_align_lmrks_mask_img)

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
            self.align_mode = lib_csw.DynamicSingleSwitch.Client()
            self.face_coverage = lib_csw.Number.Client()
            self.resolution = lib_csw.Number.Client()
            self.exclude_moving_parts = lib_csw.Flag.Client()
            self.head_mode = lib_csw.Flag.Client()
            self.freeze_z_rotation = lib_csw.Flag.Client()
            self.x_offset = lib_csw.Number.Client()
            self.y_offset = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.align_mode = lib_csw.DynamicSingleSwitch.Host()
            self.face_coverage = lib_csw.Number.Host()
            self.resolution = lib_csw.Number.Host()
            self.exclude_moving_parts = lib_csw.Flag.Host()
            self.head_mode = lib_csw.Flag.Host()
            self.freeze_z_rotation = lib_csw.Flag.Host()
            self.x_offset = lib_csw.Number.Host()
            self.y_offset = lib_csw.Number.Host()

class WorkerState(BackendWorkerState):
    align_mode = None
    face_coverage : float = None
    resolution    : int = None
    exclude_moving_parts : bool = None
    head_mode : bool = None
    freeze_z_rotation : bool = None
    x_offset : float = None
    y_offset : float = None
