import time
from enum import IntEnum

import numexpr as ne
import numpy as np
from xlib import avecl as lib_cl
from xlib import os as lib_os
from xlib.image import color_transfer as lib_ct
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

        cs.device.set_choices( ['CPU'] + lib_cl.get_available_devices_info(), none_choice_name='@misc.menu_select')

        cs.device.select(state.device if state.device is not None else 'CPU')


    def on_cs_device(self, idxs, device : lib_cl.DeviceInfo):
        state, cs = self.get_state(), self.get_control_sheet()
        if device is not None and state.device == device:
            if device != 'CPU':
                dev = lib_cl.get_device(device)
                dev.set_target_memory_usage(mb=512)
                lib_cl.set_default_device(dev)

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

            cs.color_transfer.call_on_selected(self.on_cs_color_transfer)
            cs.color_transfer.enable()
            cs.color_transfer.set_choices(['none','rct'])
            cs.color_transfer.select(state.color_transfer if state.color_transfer is not None else 'none')

            cs.interpolation.call_on_selected(self.on_cs_interpolation)
            cs.interpolation.enable()
            cs.interpolation.set_choices(['bilinear','bicubic','lanczos4'], none_choice_name=None)
            cs.interpolation.select(state.interpolation if state.interpolation is not None else 'bilinear')

            cs.face_opacity.enable()
            cs.face_opacity.set_config(lib_csw.Number.Config(min=0.0, max=1.0, step=0.01, decimals=2, allow_instant_update=True))
            cs.face_opacity.set_number(state.face_opacity if state.face_opacity is not None else 1.0)

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

    def on_cs_color_transfer(self, idx, color_transfer):
        state, cs = self.get_state(), self.get_control_sheet()
        state.color_transfer = color_transfer
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_interpolation(self, idx, interpolation):
        state, cs = self.get_state(), self.get_control_sheet()
        state.interpolation = interpolation
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_opacity(self, face_opacity):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.face_opacity.get_config()
        face_opacity = state.face_opacity = float(np.clip(face_opacity, cfg.min, cfg.max))
        cs.face_opacity.set_number(face_opacity)
        self.save_state()
        self.reemit_frame_signal.send()

    _cpu_interp = {'bilinear' : ImageProcessor.Interpolation.LINEAR,
                   'bicubic'  : ImageProcessor.Interpolation.CUBIC,
                   'lanczos4' : ImageProcessor.Interpolation.LANCZOS4}
    def _merge_on_cpu(self, frame_image, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height ):
        state = self.get_state()

        interpolation = self._cpu_interp[state.interpolation]

        frame_image = ImageProcessor(frame_image).to_ufloat32().get_image('HWC')
        face_align_mask_img = ImageProcessor(face_align_mask_img).to_ufloat32().get_image('HW')
        face_swap_mask_img = ImageProcessor(face_swap_mask_img).to_ufloat32().get_image('HW')

        if state.face_mask_type == FaceMaskType.SRC:
            face_mask = face_align_mask_img
        elif state.face_mask_type == FaceMaskType.CELEB:
            face_mask = face_swap_mask_img
        elif state.face_mask_type == FaceMaskType.SRC_M_CELEB:
            face_mask = face_align_mask_img*face_swap_mask_img

        # Combine face mask
        face_mask = ImageProcessor(face_mask).erode_blur(state.face_mask_erode, state.face_mask_blur, fade_to_border=True).get_image('HWC')

        frame_face_mask = ImageProcessor(face_mask).warpAffine(aligned_to_source_uni_mat, frame_width, frame_height).clip2( (1.0/255.0), 0.0, 1.0, 1.0).get_image('HWC')

        face_swap_img = ImageProcessor(face_swap_img).to_ufloat32().get_image('HWC')

        if state.color_transfer == 'rct':
            face_align_img = ImageProcessor(face_align_img).to_ufloat32().get_image('HWC')
            face_swap_img = lib_ct.rct(face_swap_img, face_align_img, target_mask=face_mask, source_mask=face_mask)

        frame_face_swap_img = ImageProcessor(face_swap_img).warpAffine(aligned_to_source_uni_mat, frame_width, frame_height, interpolation=interpolation).get_image('HWC')

        # Combine final frame
        opacity = state.face_opacity
        if opacity == 1.0:
            frame_final = ne.evaluate('frame_image*(1.0-frame_face_mask) + frame_face_swap_img*frame_face_mask')
        else:
            frame_final = ne.evaluate('frame_image*(1.0-frame_face_mask) + frame_image*frame_face_mask*(1.0-opacity) + frame_face_swap_img*frame_face_mask*opacity')

        return frame_final

    _gpu_interp = {'bilinear' : lib_cl.EInterpolation.LINEAR,
                   'bicubic'  : lib_cl.EInterpolation.CUBIC,
                   'lanczos4' : lib_cl.EInterpolation.LANCZOS4}

    def _merge_on_gpu(self, frame_image, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height ):
        state = self.get_state()
        interpolation = self._gpu_interp[state.interpolation]

        if state.face_mask_type == FaceMaskType.SRC:
            face_mask_t = lib_cl.Tensor.from_value(face_align_mask_img).transpose( (2,0,1), op_text='O = (I < 128 ? 0 : 1);', dtype=np.uint8)
        elif state.face_mask_type == FaceMaskType.CELEB:
            face_mask_t = lib_cl.Tensor.from_value(face_swap_mask_img).transpose( (2,0,1), op_text='O = (I < 128 ? 0 : 1);', dtype=np.uint8)

        elif state.face_mask_type == FaceMaskType.SRC_M_CELEB:
            face_mask_t = lib_cl.any_wise('float X = (((float)I0) / 255.0) * (((float)I1) / 255.0); O = (X <= 0.5 ? 0 : 1);',
                                          lib_cl.Tensor.from_value(face_align_mask_img),
                                          lib_cl.Tensor.from_value(face_swap_mask_img),
                                          dtype=np.uint8).transpose( (2,0,1) )

        face_mask_t = lib_cl.binary_morph(face_mask_t, state.face_mask_erode, state.face_mask_blur, fade_to_border=True, dtype=np.float32)
        face_swap_img_t  = lib_cl.Tensor.from_value(face_swap_img ).transpose( (2,0,1), op_text='O = ((O_TYPE)I) / 255.0', dtype=np.float32)

        if state.color_transfer == 'rct':
            face_align_img_t = lib_cl.Tensor.from_value(face_align_img).transpose( (2,0,1), op_text='O = ((O_TYPE)I) / 255.0', dtype=np.float32)
            face_swap_img_t = lib_cl.rct(face_swap_img_t, face_align_img_t, target_mask_t=face_mask_t, source_mask_t=face_mask_t)

        frame_face_mask_t     = lib_cl.remap_np_affine(face_mask_t,     aligned_to_source_uni_mat, interpolation=lib_cl.EInterpolation.LINEAR, output_size=(frame_height, frame_width), post_op_text='O = (O <= (1.0/255.0) ? 0.0 : O > 1.0 ? 1.0 : O);' )
        frame_face_swap_img_t = lib_cl.remap_np_affine(face_swap_img_t, aligned_to_source_uni_mat, interpolation=interpolation, output_size=(frame_height, frame_width), post_op_text='O = clamp(O, 0.0, 1.0);' )

        frame_image_t = lib_cl.Tensor.from_value(frame_image).transpose( (2,0,1) )

        opacity = state.face_opacity
        if opacity == 1.0:
            frame_final_t = lib_cl.any_wise('float I0f = (((float)I0) / 255.0); O = I0f*(1.0-I1) + I2*I1', frame_image_t, frame_face_mask_t, frame_face_swap_img_t, dtype=np.float32)
        else:
            frame_final_t = lib_cl.any_wise('float I0f = (((float)I0) / 255.0); O = I0f*(1.0-I1) + I0f*I1*(1.0-I3) + I2*I1*I3', frame_image_t, frame_face_mask_t, frame_face_swap_img_t, opacity, dtype=np.float32)

        return frame_final_t.transpose( (1,2,0) ).np()

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                frame_image_name = bcd.get_frame_image_name()
                frame_image = bcd.get_image(frame_image_name)

                if frame_image is not None:
                    for fsi in bcd.get_face_swap_info_list():
                        face_align_img      = bcd.get_image(fsi.face_align_image_name)
                        face_align_mask_img = bcd.get_image(fsi.face_align_mask_name)
                        face_swap_img       = bcd.get_image(fsi.face_swap_image_name)
                        face_swap_mask_img  = bcd.get_image(fsi.face_swap_mask_name)
                        image_to_align_uni_mat = fsi.image_to_align_uni_mat

                        if all_is_not_None(face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, image_to_align_uni_mat):
                            face_height, face_width = face_align_img.shape[:2]
                            frame_height, frame_width = frame_image.shape[:2]
                            aligned_to_source_uni_mat = image_to_align_uni_mat.invert()
                            aligned_to_source_uni_mat = aligned_to_source_uni_mat.source_translated(-state.face_x_offset, -state.face_y_offset)
                            aligned_to_source_uni_mat = aligned_to_source_uni_mat.source_scaled_around_center(state.face_scale,state.face_scale)
                            aligned_to_source_uni_mat = aligned_to_source_uni_mat.to_exact_mat (face_width, face_height, frame_width, frame_height)

                            if state.device == 'CPU':
                                merged_frame = self._merge_on_cpu(frame_image, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height )
                            else:
                                merged_frame = self._merge_on_gpu(frame_image, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height )
                            # keep image in float32 in order not to extra load FaceMerger

                            merged_image_name = f'{frame_image_name}_merged'
                            bcd.set_merged_image_name(merged_image_name)
                            bcd.set_image(merged_image_name, merged_frame)
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
            self.color_transfer = lib_csw.DynamicSingleSwitch.Client()
            self.interpolation = lib_csw.DynamicSingleSwitch.Client()
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
            self.color_transfer = lib_csw.DynamicSingleSwitch.Host()
            self.interpolation = lib_csw.DynamicSingleSwitch.Host()
            self.face_opacity = lib_csw.Number.Host()

class WorkerState(BackendWorkerState):
    device : lib_cl.DeviceInfo = None
    face_x_offset : float = None
    face_y_offset : float = None
    face_scale : float = None
    face_mask_type = None
    face_mask_erode : int = None
    face_mask_blur : int = None
    color_transfer = None
    interpolation = None
    face_opacity : float = None
