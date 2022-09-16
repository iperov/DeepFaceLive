import time
from pathlib import Path

import numpy as np
from modelhub.onnx import LIA
from xlib import cv as lib_cv2
from xlib import os as lib_os
from xlib import path as lib_path
from xlib.image.ImageProcessor import ImageProcessor
from xlib.mp import csw as lib_csw

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class FaceAnimator(BackendHost):
    def __init__(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, animatables_path : Path, backend_db : BackendDB = None,
                  id : int = 0):
        self._id = id
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceAnimatorWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out, animatables_path])

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

    def _get_name(self):
        return super()._get_name()

class FaceAnimatorWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, animatables_path : Path):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.animatables_path = animatables_path

        self.pending_bcd = None

        self.lia_model : LIA = None

        self.animatable_img = None
        self.driving_ref_motion = None

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()

        cs.device.call_on_selected(self.on_cs_device)
        cs.animatable.call_on_selected(self.on_cs_animatable)

        cs.animator_face_id.call_on_number(self.on_cs_animator_face_id)
        cs.relative_power.call_on_number(self.on_cs_relative_power)
        cs.update_animatables.call_on_signal(self.update_animatables)
        cs.reset_reference_pose.call_on_signal(self.on_cs_reset_reference_pose)

        cs.device.enable()
        cs.device.set_choices( LIA.get_available_devices(), none_choice_name='@misc.menu_select')
        cs.device.select(state.device)

    def update_animatables(self):
        state, cs = self.get_state(), self.get_control_sheet()
        cs.animatable.set_choices([animatable_path.name for animatable_path in lib_path.get_files_paths(self.animatables_path, extensions=['.jpg','.jpeg','.png'])], none_choice_name='@misc.menu_select')


    def on_cs_device(self, idx, device):
        state, cs = self.get_state(), self.get_control_sheet()
        if device is not None and state.device == device:
            self.lia_model = LIA(device)

            cs.animatable.enable()
            self.update_animatables()
            cs.animatable.select(state.animatable)

            cs.animator_face_id.enable()
            cs.animator_face_id.set_config(lib_csw.Number.Config(min=0, max=16, step=1, decimals=0, allow_instant_update=True))
            cs.animator_face_id.set_number(state.animator_face_id if state.animator_face_id is not None else 0)
            
            cs.relative_power.enable()
            cs.relative_power.set_config(lib_csw.Number.Config(min=0.0, max=2.0, step=0.01, decimals=2, allow_instant_update=True))
            cs.relative_power.set_number(state.relative_power if state.relative_power is not None else 1.0)

            cs.update_animatables.enable()
            cs.reset_reference_pose.enable()
        else:
            state.device = device
            self.save_state()
            self.restart()

    def on_cs_animatable(self, idx, animatable):
        state, cs = self.get_state(), self.get_control_sheet()

        state.animatable = animatable
        self.animatable_img = None
        self.driving_ref_motion = None

        if animatable is not None:
            try:
                W,H = self.lia_model.get_input_size()
                ip = ImageProcessor(lib_cv2.imread(self.animatables_path / animatable))
                ip.fit_in(TW=W, TH=H, pad_to_target=True, allow_upscale=True)

                self.animatable_img = ip.get_image('HWC')
            except Exception as e:
                cs.animatable.unselect()

        self.save_state()
        self.reemit_frame_signal.send()


    def on_cs_animator_face_id(self, animator_face_id):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.animator_face_id.get_config()
        animator_face_id = state.animator_face_id = int(np.clip(animator_face_id, cfg.min, cfg.max))
        cs.animator_face_id.set_number(animator_face_id)
        self.save_state()
        self.reemit_frame_signal.send()
    def on_cs_relative_power(self, relative_power):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.relative_power.get_config()
        relative_power = state.relative_power = float(np.clip(relative_power, cfg.min, cfg.max))
        cs.relative_power.set_number(relative_power)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_reset_reference_pose(self):
        self.driving_ref_motion = None
        self.reemit_frame_signal.send()

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                lia_model = self.lia_model
                if lia_model is not None and self.animatable_img is not None:

                    for i, fsi in enumerate(bcd.get_face_swap_info_list()):
                        if state.animator_face_id == i:
                            face_align_image = bcd.get_image(fsi.face_align_image_name)
                            if face_align_image is not None:

                                _,H,W,_ = ImageProcessor(face_align_image).get_dims()

                                if self.driving_ref_motion is None:
                                    self.driving_ref_motion = lia_model.extract_motion(face_align_image)

                                anim_image = lia_model.generate(self.animatable_img, face_align_image, self.driving_ref_motion, power=state.relative_power)
                                anim_image = ImageProcessor(anim_image).resize((W,H)).get_image('HWC')

                                fsi.face_swap_image_name = f'{fsi.face_align_image_name}_swapped'
                                bcd.set_image(fsi.face_swap_image_name, anim_image)
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
            self.animatable = lib_csw.DynamicSingleSwitch.Client()
            self.animator_face_id = lib_csw.Number.Client()
            self.update_animatables = lib_csw.Signal.Client()
            self.reset_reference_pose = lib_csw.Signal.Client()
            self.relative_power = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.animatable = lib_csw.DynamicSingleSwitch.Host()
            self.animator_face_id = lib_csw.Number.Host()
            self.update_animatables = lib_csw.Signal.Host()
            self.reset_reference_pose = lib_csw.Signal.Host()
            self.relative_power = lib_csw.Number.Host()

class WorkerState(BackendWorkerState):
    device = None
    animatable : str = None
    animator_face_id : int = None
    relative_power : float = None
