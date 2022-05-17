import time

import cv2
import numexpr as ne
import numpy as np
from xlib import avecl as lib_cl
from xlib import os as lib_os
from xlib.image import ImageProcessor
from xlib.image import color_transfer as lib_ct
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


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
        self.out_merged_frame = None

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()
        cs.device.call_on_selected(self.on_cs_device)
        cs.face_x_offset.call_on_number(self.on_cs_face_x_offset)
        cs.face_y_offset.call_on_number(self.on_cs_face_y_offset)
        cs.face_scale.call_on_number(self.on_cs_face_scale)

        cs.face_mask_source.call_on_flag(self.on_cs_face_mask_source)
        cs.face_mask_celeb.call_on_flag(self.on_cs_face_mask_celeb)
        cs.face_mask_lmrks.call_on_flag(self.on_cs_face_mask_lmrks)

        cs.face_mask_erode.call_on_number(self.on_cs_mask_erode)
        cs.face_mask_blur.call_on_number(self.on_cs_mask_blur)

        cs.color_compression.call_on_number(self.on_cs_color_compression)
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

            cs.face_mask_source.enable()
            cs.face_mask_source.set_flag(state.face_mask_source if state.face_mask_source is not None else True)
            cs.face_mask_celeb.enable()
            cs.face_mask_celeb.set_flag(state.face_mask_celeb if state.face_mask_celeb is not None else True)
            cs.face_mask_lmrks.enable()
            cs.face_mask_lmrks.set_flag(state.face_mask_lmrks if state.face_mask_lmrks is not None else False)

            cs.face_mask_erode.enable()
            cs.face_mask_erode.set_config(lib_csw.Number.Config(min=-400, max=400, step=1, decimals=0, allow_instant_update=True))
            cs.face_mask_erode.set_number(state.face_mask_erode if state.face_mask_erode is not None else 5.0)

            cs.face_mask_blur.enable()
            cs.face_mask_blur.set_config(lib_csw.Number.Config(min=0, max=400, step=1, decimals=0, allow_instant_update=True))
            cs.face_mask_blur.set_number(state.face_mask_blur if state.face_mask_blur is not None else 25.0)

            cs.color_transfer.call_on_selected(self.on_cs_color_transfer)
            cs.color_transfer.enable()
            cs.color_transfer.set_choices(['none','rct'])
            cs.color_transfer.select(state.color_transfer if state.color_transfer is not None else 'rct')

            cs.interpolation.call_on_selected(self.on_cs_interpolation)
            cs.interpolation.enable()
            cs.interpolation.set_choices(['bilinear','bicubic','lanczos4'], none_choice_name=None)
            cs.interpolation.select(state.interpolation if state.interpolation is not None else 'bilinear')

            cs.color_compression.enable()
            cs.color_compression.set_config(lib_csw.Number.Config(min=0.0, max=127.0, step=0.1, decimals=1, allow_instant_update=True))
            cs.color_compression.set_number(state.color_compression if state.color_compression is not None else 1.0)

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

    def on_cs_face_mask_source(self, face_mask_source):
        state, cs = self.get_state(), self.get_control_sheet()
        state.face_mask_source = face_mask_source
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_mask_celeb(self, face_mask_celeb):
        state, cs = self.get_state(), self.get_control_sheet()
        state.face_mask_celeb = face_mask_celeb
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_face_mask_lmrks(self, face_mask_lmrks):
        state, cs = self.get_state(), self.get_control_sheet()
        state.face_mask_lmrks = face_mask_lmrks
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

    def on_cs_color_compression(self, color_compression):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.color_compression.get_config()
        color_compression = state.color_compression = float(np.clip(color_compression, cfg.min, cfg.max))
        cs.color_compression.set_number(color_compression)
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
    def _merge_on_cpu(self, frame_image, face_resolution, face_align_img, face_align_mask_img, face_align_lmrks_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height, do_color_compression ):
        state = self.get_state()

        interpolation = self._cpu_interp[state.interpolation]

        frame_image = ImageProcessor(frame_image).to_ufloat32().get_image('HWC')

        masks = []
        if state.face_mask_source:
            masks.append( ImageProcessor(face_align_mask_img).to_ufloat32().get_image('HW') )
        if state.face_mask_celeb:
            masks.append( ImageProcessor(face_swap_mask_img).to_ufloat32().get_image('HW') )
        if state.face_mask_lmrks:
            masks.append( ImageProcessor(face_align_lmrks_mask_img).to_ufloat32().get_image('HW') )

        masks_count = len(masks)
        if masks_count == 0:
            face_mask = np.ones(shape=(face_resolution, face_resolution), dtype=np.float32)
        else:
            face_mask = masks[0]
            for i in range(1, masks_count):
                face_mask *= masks[i]

        # Combine face mask
        face_mask = ImageProcessor(face_mask).erode_blur(state.face_mask_erode, state.face_mask_blur, fade_to_border=True).get_image('HWC')
        frame_face_mask = ImageProcessor(face_mask).warp_affine(aligned_to_source_uni_mat, frame_width, frame_height).clip2( (1.0/255.0), 0.0, 1.0, 1.0).get_image('HWC')

        face_swap_ip = ImageProcessor(face_swap_img).to_ufloat32()

        if state.color_transfer == 'rct':            
            face_swap_img = face_swap_ip.rct(like=face_align_img, mask=face_mask, like_mask=face_mask)

        frame_face_swap_img = face_swap_ip.warp_affine(aligned_to_source_uni_mat, frame_width, frame_height, interpolation=interpolation).get_image('HWC')

        # Combine final frame
        opacity = np.float32(state.face_opacity)
        one_f = np.float32(1.0)
        if opacity == 1.0:
            out_merged_frame = ne.evaluate('frame_image*(one_f-frame_face_mask) + frame_face_swap_img*frame_face_mask')
        else:
            out_merged_frame = ne.evaluate('frame_image*(one_f-frame_face_mask) + frame_image*frame_face_mask*(one_f-opacity) + frame_face_swap_img*frame_face_mask*opacity')

        if do_color_compression and state.color_compression != 0:
            color_compression = max(4, (127.0 - state.color_compression) )
            out_merged_frame *= color_compression
            np.floor(out_merged_frame, out=out_merged_frame)
            out_merged_frame /= color_compression
            out_merged_frame += 2.0 / color_compression

        return out_merged_frame

    _gpu_interp = {'bilinear' : lib_cl.EInterpolation.LINEAR,
                   'bicubic'  : lib_cl.EInterpolation.CUBIC,
                   'lanczos4' : lib_cl.EInterpolation.LANCZOS4}

    _n_mask_multiply_op_text = [ f"float X = {'*'.join([f'(((float)I{i}) / 255.0)' for i in range(n)])}; O = (X <= 0.5 ? 0 : 1);" for n in range(5) ]

    def _merge_on_gpu(self, frame_image, face_resolution, face_align_img, face_align_mask_img, face_align_lmrks_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height, do_color_compression ):
        state = self.get_state()
        interpolation = self._gpu_interp[state.interpolation]

        masks = []
        if state.face_mask_source:
            masks.append( lib_cl.Tensor.from_value(face_align_mask_img) )
        if state.face_mask_celeb:
            masks.append( lib_cl.Tensor.from_value(face_swap_mask_img) )
        if state.face_mask_lmrks:
            masks.append( lib_cl.Tensor.from_value(face_align_lmrks_mask_img) )

        masks_count = len(masks)
        if masks_count == 0:
            face_mask_t = lib_cl.Tensor(shape=(face_resolution, face_resolution), dtype=np.float32, initializer=lib_cl.InitConst(1.0))
        else:
            face_mask_t = lib_cl.any_wise(FaceMergerWorker._n_mask_multiply_op_text[masks_count], *masks, dtype=np.uint8).transpose( (2,0,1) )

        face_mask_t = lib_cl.binary_morph(face_mask_t, state.face_mask_erode, state.face_mask_blur, fade_to_border=True, dtype=np.float32)
        face_swap_img_t  = lib_cl.Tensor.from_value(face_swap_img ).transpose( (2,0,1), op_text='O = ((O_TYPE)I) / 255.0', dtype=np.float32)

        if state.color_transfer == 'rct':
            face_align_img_t = lib_cl.Tensor.from_value(face_align_img).transpose( (2,0,1), op_text='O = ((O_TYPE)I) / 255.0', dtype=np.float32)
            face_swap_img_t = lib_cl.rct(face_swap_img_t, face_align_img_t, target_mask_t=face_mask_t, source_mask_t=face_mask_t)

        frame_face_mask_t     = lib_cl.remap_np_affine(face_mask_t,     aligned_to_source_uni_mat, interpolation=lib_cl.EInterpolation.LINEAR, output_size=(frame_height, frame_width), post_op_text='O = (O <= (1.0/255.0) ? 0.0 : O > 1.0 ? 1.0 : O);' )
        frame_face_swap_img_t = lib_cl.remap_np_affine(face_swap_img_t, aligned_to_source_uni_mat, interpolation=interpolation, output_size=(frame_height, frame_width), post_op_text='O = clamp(O, 0.0, 1.0);' )

        frame_image_t = lib_cl.Tensor.from_value(frame_image).transpose( (2,0,1), op_text='O = ((float)I) / 255.0;' if frame_image.dtype == np.uint8 else None,
                                                                                  dtype=np.float32 if frame_image.dtype == np.uint8 else None)

        opacity = state.face_opacity
        if opacity == 1.0:
            frame_final_t = lib_cl.any_wise('O = I0*(1.0-I1) + I2*I1', frame_image_t, frame_face_mask_t, frame_face_swap_img_t, dtype=np.float32)
        else:
            frame_final_t = lib_cl.any_wise('O = I0*(1.0-I1) + I0*I1*(1.0-I3) + I2*I1*I3', frame_image_t, frame_face_mask_t, frame_face_swap_img_t, np.float32(opacity), dtype=np.float32)

        if do_color_compression and state.color_compression != 0:
            color_compression = max(4, (127.0 - state.color_compression) )
            frame_final_t = lib_cl.any_wise('O = ( floor(I0 * I1) / I1 ) + (2.0 / I1);', frame_final_t, np.float32(color_compression))

        return frame_final_t.transpose( (1,2,0) ).np()

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                frame_image_name = bcd.get_frame_image_name()
                merged_frame = bcd.get_image(frame_image_name)

                if merged_frame is not None:
                    fsi_list = bcd.get_face_swap_info_list()
                    fsi_list_len = len(fsi_list)
                    has_merged_faces = False

                    for fsi_id, fsi in enumerate(fsi_list):

                        face_anim_img             = bcd.get_image(fsi.face_anim_image_name)
                        if face_anim_img is not None:
                            has_merged_faces = True
                            merged_frame = face_anim_img
                        else:

                            image_to_align_uni_mat = fsi.image_to_align_uni_mat
                            face_resolution        = fsi.face_resolution

                            face_align_img            = bcd.get_image(fsi.face_align_image_name)
                            face_align_lmrks_mask_img = bcd.get_image(fsi.face_align_lmrks_mask_name)
                            face_align_mask_img       = bcd.get_image(fsi.face_align_mask_name)
                            face_swap_img             = bcd.get_image(fsi.face_swap_image_name)
                            face_swap_mask_img        = bcd.get_image(fsi.face_swap_mask_name)

                            if all_is_not_None(face_resolution, face_align_img, face_align_mask_img, face_swap_img, face_swap_mask_img, image_to_align_uni_mat):
                                has_merged_faces = True
                                face_height, face_width = face_align_img.shape[:2]
                                frame_height, frame_width = merged_frame.shape[:2]
                                aligned_to_source_uni_mat = image_to_align_uni_mat.invert()
                                aligned_to_source_uni_mat = aligned_to_source_uni_mat.source_translated(-state.face_x_offset, -state.face_y_offset)
                                aligned_to_source_uni_mat = aligned_to_source_uni_mat.source_scaled_around_center(state.face_scale,state.face_scale)
                                aligned_to_source_uni_mat = aligned_to_source_uni_mat.to_exact_mat (face_width, face_height, frame_width, frame_height)

                                do_color_compression = fsi_id == fsi_list_len-1
                                if state.device == 'CPU':
                                    merged_frame = self._merge_on_cpu(merged_frame, face_resolution, face_align_img, face_align_mask_img, face_align_lmrks_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height, do_color_compression=do_color_compression )
                                else:
                                    merged_frame = self._merge_on_gpu(merged_frame, face_resolution, face_align_img, face_align_mask_img, face_align_lmrks_mask_img, face_swap_img, face_swap_mask_img, aligned_to_source_uni_mat, frame_width, frame_height, do_color_compression=do_color_compression )

                    if has_merged_faces:
                        # keep image in float32 in order not to extra load FaceMerger
                        merged_image_name = f'{frame_image_name}_merged'
                        bcd.set_merged_image_name(merged_image_name)
                        bcd.set_image(merged_image_name, merged_frame)

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
            self.face_mask_source = lib_csw.Flag.Client()
            self.face_mask_celeb = lib_csw.Flag.Client()
            self.face_mask_lmrks = lib_csw.Flag.Client()

            self.face_mask_x_offset = lib_csw.Number.Client()
            self.face_mask_y_offset = lib_csw.Number.Client()
            self.face_mask_scale = lib_csw.Number.Client()
            self.face_mask_erode = lib_csw.Number.Client()
            self.face_mask_blur = lib_csw.Number.Client()
            self.color_transfer = lib_csw.DynamicSingleSwitch.Client()
            self.interpolation = lib_csw.DynamicSingleSwitch.Client()
            self.color_compression = lib_csw.Number.Client()
            self.face_opacity = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.face_x_offset = lib_csw.Number.Host()
            self.face_y_offset = lib_csw.Number.Host()
            self.face_scale = lib_csw.Number.Host()
            self.face_mask_source = lib_csw.Flag.Host()
            self.face_mask_celeb = lib_csw.Flag.Host()
            self.face_mask_lmrks = lib_csw.Flag.Host()

            self.face_mask_erode = lib_csw.Number.Host()
            self.face_mask_blur = lib_csw.Number.Host()
            self.color_transfer = lib_csw.DynamicSingleSwitch.Host()
            self.interpolation = lib_csw.DynamicSingleSwitch.Host()

            self.color_compression = lib_csw.Number.Host()
            self.face_opacity = lib_csw.Number.Host()

class WorkerState(BackendWorkerState):
    device : lib_cl.DeviceInfo = None
    face_x_offset : float = None
    face_y_offset : float = None
    face_scale : float = None

    face_mask_source : bool = None
    face_mask_celeb : bool = None
    face_mask_lmrks : bool = None

    face_mask_erode : int = None
    face_mask_blur : int = None
    color_transfer = None
    interpolation = None
    color_compression : int = None
    face_opacity : float = None

# out_merged_frame = self.out_merged_frame
# if out_merged_frame is None or out_merged_frame.shape[:2] != (frame_height, frame_width):
#     out_merged_frame = self.out_merged_frame = np.empty_like(frame_image, np.float32)
