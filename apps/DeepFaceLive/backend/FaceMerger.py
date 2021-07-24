import time
from enum import IntEnum

import numexpr as ne
import numpy as np
from xlib import cupy as lib_cp
from xlib import os as lib_os
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class FaceMaskType(IntEnum):
    SRC = 0
    CELEB = 1
    SRC_M_CELEB = 2

FaceMaskTypeNames = ['@FaceMerger.FaceMaskType.SRC','@FaceMerger.FaceMaskType.CELEB','@FaceMerger.FaceMaskType.SRC_M_CELEB']

class FaceMerger(BackendHost):

    def __init__(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out  : BackendConnection, backend_db : BackendDB = None):
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceMergerWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

class FaceMergerWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection):


        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.pending_bcd = None
        self.is_gpu = False
        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()
        cs.device.call_on_selected(self.on_cs_device)
        cs.face_x_offset.call_on_number(self.on_cs_face_x_offset)
        cs.face_y_offset.call_on_number(self.on_cs_face_y_offset)
        cs.face_scale.call_on_number(self.on_cs_face_scale)
        cs.face_mask_erode.call_on_number(self.on_cs_mask_erode)
        cs.face_mask_blur.call_on_number(self.on_cs_mask_blur)
        cs.face_opacity.call_on_number(self.on_cs_face_opacity)

        cs.device.enable()
        cs.device.set_choices( ['CPU'] + lib_cp.get_available_devices(), none_choice_name='@misc.menu_select')

        cs.device.select(state.device if state.device is not None else 'CPU')


    def on_cs_device(self, idxs, device : lib_cp.CuPyDeviceInfo):
        state, cs = self.get_state(), self.get_control_sheet()
        if device is not None and state.device == device:
            cs.face_x_offset.enable()
            cs.face_x_offset.set_config(lib_csw.Number.Config(min=-0.5, max=0.5, step=0.001, decimals=3, allow_instant_update=True))
            cs.face_x_offset.set_number(state.face_x_offset if state.face_x_offset is not None else 0.0)

            cs.face_y_offset.enable()
            cs.face_y_offset.set_config(lib_csw.Number.Config(min=-0.5, max=0.5, step=0.001, decimals=3, allow_instant_update=True))
            cs.face_y_offset.set_number(state.face_y_offset if state.face_y_offset is not None else 0.0)

            cs.face_scale.enable()
            cs.face_scale.set_config(lib_csw.Number.Config(min=0.5, max=1.5, step=0.01, decimals=2, allow_instant_update=True))
            cs.face_scale.set_number(state.face_scale if state.face_scale is not None else 1.0)

            cs.face_mask_type.call_on_selected(self.on_cs_face_mask_type)
            cs.face_mask_type.enable()
            cs.face_mask_type.set_choices(FaceMaskType, FaceMaskTypeNames, none_choice_name=None)
            cs.face_mask_type.select(state.face_mask_type if state.face_mask_type is not None else FaceMaskType.SRC_M_CELEB)

            cs.face_mask_erode.enable()
            cs.face_mask_erode.set_config(lib_csw.Number.Config(min=-400, max=400, step=1, decimals=0, allow_instant_update=True))
            cs.face_mask_erode.set_number(state.face_mask_erode if state.face_mask_erode is not None else 5.0)

            cs.face_mask_blur.enable()
            cs.face_mask_blur.set_config(lib_csw.Number.Config(min=0, max=400, step=1, decimals=0, allow_instant_update=True))
            cs.face_mask_blur.set_number(state.face_mask_blur if state.face_mask_blur is not None else 25.0)

            cs.face_opacity.enable()
            cs.face_opacity.set_config(lib_csw.Number.Config(min=0.0, max=1.0, step=0.01, decimals=2, allow_instant_update=True))
            cs.face_opacity.set_number(state.face_opacity if state.face_opacity is not None else 1.0)

            if device != 'CPU':
                self.is_gpu = True

                global cp
                import cupy as cp # BUG eats 1.8Gb paging file per process, so import on demand
                cp.cuda.Device( device.get_index() ).use()

                self.cp_mask_clip_kernel = cp.ElementwiseKernel('T x', 'T z', 'z = x < 0.004 ? 0 : x > 1.0 ? 1.0 : x', 'mask_clip_kernel')
                self.cp_merge_kernel = cp.ElementwiseKernel('T bg, T face, T mask', 'T z', 'z = bg*(1.0-mask) + face*mask', 'merge_kernel')
                self.cp_merge_kernel_opacity = cp.ElementwiseKernel('T bg, T face, T mask, T opacity', 'T z', 'z = bg*(1.0-mask) + bg*mask*(1.0-opacity) + face*mask*opacity',  'merge_kernel_opacity')

        else:
            state.device = device
            self.save_state()
            self.restart()


    def on_cs_face_x_offset(self, face_x_offset):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_x_offset.get_config()
        face_x_offset = state.face_x_offset = float(np.clip(face_x_offset, cfg.min, cfg.max))
        cs.face_x_offset.set_number(face_x_offset)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_y_offset(self, face_y_offset):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_y_offset.get_config()
        face_y_offset = state.face_y_offset = float(np.clip(face_y_offset, cfg.min, cfg.max))
        cs.face_y_offset.set_number(face_y_offset)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_scale(self, face_scale):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_scale.get_config()
        face_scale = state.face_scale = float(np.clip(face_scale, cfg.min, cfg.max))
        cs.face_scale.set_number(face_scale)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_mask_type(self, idx, face_mask_type):
        state, cs = self.get_state(), self.get_control_sheet()
        state.face_mask_type = face_mask_type
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_mask_erode(self, face_mask_erode):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_mask_erode.get_config()
        face_mask_erode = state.face_mask_erode = int(np.clip(face_mask_erode, cfg.min, cfg.max))
        cs.face_mask_erode.set_number(face_mask_erode)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_mask_blur(self, face_mask_blur):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_mask_blur.get_config()
        face_mask_blur = state.face_mask_blur = int(np.clip(face_mask_blur, cfg.min, cfg.max))
        cs.face_mask_blur.set_number(face_mask_blur)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_opacity(self, face_opacity):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_opacity.get_config()
        face_opacity = state.face_opacity = float(np.clip(face_opacity, cfg.min, cfg.max))
        cs.face_opacity.set_number(face_opacity)
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

                if frame_image is not None:
                    for face_mark in bcd.get_face_mark_list():
                        face_align = face_mark.get_face_align()
                        if face_align is not None:
                            face_swap = face_align.get_face_swap()
                            face_align_mask = face_align.get_face_mask()

                            if face_swap is not None:
                                face_swap_mask = face_swap.get_face_mask()
                                if face_swap_mask is not None:

                                    face_align_img = bcd.get_image(face_align.get_image_name())
                                    face_swap_img = bcd.get_image(face_swap.get_image_name())

                                    face_align_mask_img = bcd.get_image(face_align_mask.get_image_name())
                                    face_swap_mask_img = bcd.get_image(face_swap_mask.get_image_name())
                                    source_to_aligned_uni_mat = face_align.get_source_to_aligned_uni_mat()

                                    face_mask_type = state.face_mask_type

                                    if all_is_not_None(face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, face_mask_type):
                                        face_height, face_width = face_align_img.shape[:2]

                                        if self.is_gpu:
                                            frame_image = cp.asarray(frame_image)
                                            face_align_mask_img = cp.asarray(face_align_mask_img)
                                            face_swap_mask_img = cp.asarray(face_swap_mask_img)
                                            face_swap_img = cp.asarray(face_swap_img)

                                        frame_image_ip = ImageProcessor(frame_image).to_ufloat32()
                                        frame_image, (_, frame_height, frame_width, _) = frame_image_ip.get_image('HWC'), frame_image_ip.get_dims()
                                        face_align_mask_img = ImageProcessor(face_align_mask_img).to_ufloat32().get_image('HW')
                                        face_swap_mask_img = ImageProcessor(face_swap_mask_img).to_ufloat32().get_image('HW')

                                        aligned_to_source_uni_mat = source_to_aligned_uni_mat.invert()
                                        aligned_to_source_uni_mat = aligned_to_source_uni_mat.source_translated(-state.face_x_offset, -state.face_y_offset)
                                        aligned_to_source_uni_mat = aligned_to_source_uni_mat.source_scaled_around_center(state.face_scale,state.face_scale)
                                        aligned_to_source_uni_mat = aligned_to_source_uni_mat.to_exact_mat (face_width, face_height, frame_width, frame_height)

                                        if face_mask_type == FaceMaskType.SRC:
                                            face_mask = face_align_mask_img
                                        elif face_mask_type == FaceMaskType.CELEB:
                                            face_mask = face_swap_mask_img
                                        elif face_mask_type == FaceMaskType.SRC_M_CELEB:
                                            face_mask = face_align_mask_img*face_swap_mask_img

                                        # Combine face mask
                                        face_mask_ip = ImageProcessor(face_mask).erode_blur(state.face_mask_erode, state.face_mask_blur, fade_to_border=True) \
                                                                                .warpAffine(aligned_to_source_uni_mat, frame_width, frame_height)
                                        if self.is_gpu:
                                            face_mask_ip.apply( lambda img: self.cp_mask_clip_kernel(img) )
                                        else:
                                            face_mask_ip.clip2( (1.0/255.0), 0.0, 1.0, 1.0)
                                        frame_face_mask = face_mask_ip.get_image('HWC')

                                        frame_face_swap_img = ImageProcessor(face_swap_img) \
                                                              .to_ufloat32().warpAffine(aligned_to_source_uni_mat, frame_width, frame_height).get_image('HWC')

                                        # Combine final frame
                                        opacity = state.face_opacity
                                        if self.is_gpu:
                                            if opacity == 1.0:
                                                frame_final = self.cp_merge_kernel(frame_image, frame_face_swap_img, frame_face_mask)
                                            else:
                                                frame_final = self.cp_merge_kernel_opacity(frame_image, frame_face_swap_img, frame_face_mask, opacity)
                                            frame_final = cp.asnumpy(frame_final)
                                        else:
                                            if opacity == 1.0:
                                                frame_final = ne.evaluate('frame_image*(1.0-frame_face_mask) + frame_face_swap_img*frame_face_mask')
                                            else:
                                                frame_final = ne.evaluate('frame_image*(1.0-frame_face_mask) + frame_image*frame_face_mask*(1.0-opacity) + frame_face_swap_img*frame_face_mask*opacity')

                                        # keep image in float32 in order not to extra load FaceMerger

                                        merged_frame_name = f'{frame_name}_merged'
                                        bcd.set_merged_frame_name(merged_frame_name)
                                        bcd.set_image(merged_frame_name, frame_final)
                                break

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
            self.device = lib_csw.DynamicSingleSwitch.Client()
            self.face_x_offset = lib_csw.Number.Client()
            self.face_y_offset = lib_csw.Number.Client()
            self.face_scale = lib_csw.Number.Client()
            self.face_mask_type = lib_csw.DynamicSingleSwitch.Client()
            self.face_mask_x_offset = lib_csw.Number.Client()
            self.face_mask_y_offset = lib_csw.Number.Client()
            self.face_mask_scale = lib_csw.Number.Client()
            self.face_mask_erode = lib_csw.Number.Client()
            self.face_mask_blur = lib_csw.Number.Client()
            self.face_opacity = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.face_x_offset = lib_csw.Number.Host()
            self.face_y_offset = lib_csw.Number.Host()
            self.face_scale = lib_csw.Number.Host()
            self.face_mask_type = lib_csw.DynamicSingleSwitch.Host()
            self.face_mask_erode = lib_csw.Number.Host()
            self.face_mask_blur = lib_csw.Number.Host()
            self.face_opacity = lib_csw.Number.Host()

class WorkerState(BackendWorkerState):
    device : lib_cp.CuPyDeviceInfo = None
    face_x_offset : float = None
    face_y_offset : float = None
    face_scale : float = None
    face_mask_type = None
    face_mask_erode : int = None
    face_mask_blur : int = None
    face_opacity : float = None
