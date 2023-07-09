import time
from pathlib import Path
import cv2
import numpy as np
from modelhub.onnx import InsightFace2D106, InsightFaceSwap, YoloV5Face
from xlib import cv as lib_cv2
from xlib import os as lib_os
from xlib import path as lib_path
from xlib.face import ELandmarks2D, FLandmarks2D, FRect
from xlib.image.ImageProcessor import ImageProcessor
from xlib.mp import csw as lib_csw

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class FaceSwapInsight(BackendHost):
    def __init__(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, faces_path : Path, backend_db : BackendDB = None,
                  id : int = 0):
        self._id = id
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceSwapInsightWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out, faces_path])

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

    def _get_name(self):
        return super()._get_name()

class FaceSwapInsightWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, faces_path : Path):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.faces_path = faces_path

        self.pending_bcd = None

        self.swap_model : InsightFaceSwap = None

        self.target_face_img = None
        self.face_vector = None

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()

        cs.device.call_on_selected(self.on_cs_device)
        cs.face.call_on_selected(self.on_cs_face)
        cs.adjust_c.call_on_number(self.on_cs_adjust_c)
        cs.adjust_x.call_on_number(self.on_cs_adjust_x)
        cs.adjust_y.call_on_number(self.on_cs_adjust_y)

        cs.animator_face_id.call_on_number(self.on_cs_animator_face_id)
        cs.update_faces.call_on_signal(self.update_faces)

        cs.device.enable()
        cs.device.set_choices( InsightFaceSwap.get_available_devices(), none_choice_name='@misc.menu_select')
        cs.device.select(state.device)

    def update_faces(self):
        state, cs = self.get_state(), self.get_control_sheet()
        cs.face.set_choices([face_path.name for face_path in lib_path.get_files_paths(self.faces_path, extensions=['.jpg','.jpeg','.png'])], none_choice_name='@misc.menu_select')


    def on_cs_device(self, idx, device):
        state, cs = self.get_state(), self.get_control_sheet()
        if device is not None and state.device == device:
            self.swap_model = InsightFaceSwap(device)

            self.face_detector = YoloV5Face(device)
            self.face_marker = InsightFace2D106(device)

            cs.face.enable()
            self.update_faces()
            cs.face.select(state.face)

            cs.adjust_c.enable()
            cs.adjust_c.set_config(lib_csw.Number.Config(min=1.0, max=2.0, step=0.01, decimals=2, allow_instant_update=True))
            adjust_c = state.adjust_c
            if adjust_c is None:
                adjust_c = 1.55
            cs.adjust_c.set_number(adjust_c)

            cs.adjust_x.enable()
            cs.adjust_x.set_config(lib_csw.Number.Config(min=-0.5, max=0.5, step=0.01, decimals=2, allow_instant_update=True))
            adjust_x = state.adjust_x
            if adjust_x is None:
                adjust_x = 0.0
            cs.adjust_x.set_number(adjust_x)

            cs.adjust_y.enable()
            cs.adjust_y.set_config(lib_csw.Number.Config(min=-0.5, max=0.5, step=0.01, decimals=2, allow_instant_update=True))
            adjust_y = state.adjust_y
            if adjust_y is None:
                adjust_y = -0.15
            cs.adjust_y.set_number(adjust_y)

            cs.animator_face_id.enable()
            cs.animator_face_id.set_config(lib_csw.Number.Config(min=0, max=16, step=1, decimals=0, allow_instant_update=True))
            cs.animator_face_id.set_number(state.animator_face_id if state.animator_face_id is not None else 0)

            cs.update_faces.enable()
        else:
            state.device = device
            self.save_state()
            self.restart()

    def on_cs_face(self, idx, face):
        state, cs = self.get_state(), self.get_control_sheet()

        state.face = face
        self.face_vector = None
        self.target_face_img = None

        if face is not None:
            try:
                self.target_face_img = lib_cv2.imread(self.faces_path / face)

            except Exception as e:
                cs.face.unselect()

        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_adjust_c(self, adjust_c):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.adjust_c.get_config()
        adjust_c = state.adjust_c = np.clip(adjust_c, cfg.min, cfg.max)
        cs.adjust_c.set_number(adjust_c)

        self.face_vector = None
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_adjust_x(self, adjust_x):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.adjust_x.get_config()
        adjust_x = state.adjust_x = np.clip(adjust_x, cfg.min, cfg.max)
        cs.adjust_x.set_number(adjust_x)

        self.face_vector = None
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_adjust_y(self, adjust_y):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.adjust_y.get_config()
        adjust_y = state.adjust_y = np.clip(adjust_y, cfg.min, cfg.max)
        cs.adjust_y.set_number(adjust_y)

        self.face_vector = None
        self.save_state()
        self.reemit_frame_signal.send()


    def on_cs_animator_face_id(self, animator_face_id):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.animator_face_id.get_config()
        animator_face_id = state.animator_face_id = int(np.clip(animator_face_id, cfg.min, cfg.max))
        cs.animator_face_id.set_number(animator_face_id)
        self.save_state()
        self.reemit_frame_signal.send()


    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                if self.face_vector is None and self.target_face_img is not None:
                    rects = self.face_detector.extract (self.target_face_img, threshold=0.5)[0]
                    if len(rects) > 0:
                        _,H,W,_ = ImageProcessor(self.target_face_img).get_dims()

                        u_rects = [ FRect.from_ltrb( (l/W, t/H, r/W, b/H) ) for l,t,r,b in rects ]
                        face_urect = FRect.sort_by_area_size(u_rects)[0] # sorted by largest

                        face_image, face_uni_mat = face_urect.cut(self.target_face_img, 1.6, 192)
                        lmrks = self.face_marker.extract(face_image)[0]
                        lmrks = lmrks[...,0:2] / (192,192)

                        face_ulmrks = FLandmarks2D.create (ELandmarks2D.L106, lmrks).transform(face_uni_mat, invert=True)

                        face_align_img, _ = face_ulmrks.cut(self.target_face_img, state.adjust_c,
                                                                self.swap_model.get_face_vector_input_size(),
                                                                x_offset=state.adjust_x,
                                                                y_offset=state.adjust_y)
                        self.face_vector = self.swap_model.get_face_vector(face_align_img)


                swap_model = self.swap_model
                if swap_model is not None and self.face_vector is not None:

                    for i, fsi in enumerate(bcd.get_face_swap_info_list()):
                        if state.animator_face_id == i:
                            face_align_image = bcd.get_image(fsi.face_align_image_name)
                            if face_align_image is not None:

                                _,H,W,_ = ImageProcessor(face_align_image).get_dims()

                                anim_image = swap_model.generate(face_align_image, self.face_vector)
                                anim_image = ImageProcessor(anim_image).resize((W,H)).get_image('HWC')

                                fsi.face_align_mask_name = f'{fsi.face_align_image_name}_mask'
                                fsi.face_swap_image_name = f'{fsi.face_align_image_name}_swapped'
                                fsi.face_swap_mask_name  = f'{fsi.face_swap_image_name}_mask'
                                bcd.set_image(fsi.face_swap_image_name, anim_image)

                                white_mask = np.full_like(anim_image, 255, dtype=np.uint8)
                                bcd.set_image(fsi.face_align_mask_name, white_mask)
                                bcd.set_image(fsi.face_swap_mask_name, white_mask)

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
            self.face = lib_csw.DynamicSingleSwitch.Client()
            self.animator_face_id = lib_csw.Number.Client()
            self.update_faces = lib_csw.Signal.Client()
            self.adjust_c = lib_csw.Number.Client()
            self.adjust_x = lib_csw.Number.Client()
            self.adjust_y = lib_csw.Number.Client()


    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.face = lib_csw.DynamicSingleSwitch.Host()
            self.animator_face_id = lib_csw.Number.Host()
            self.update_faces = lib_csw.Signal.Host()
            self.adjust_c = lib_csw.Number.Host()
            self.adjust_x = lib_csw.Number.Host()
            self.adjust_y = lib_csw.Number.Host()


class WorkerState(BackendWorkerState):
    device = None
    face : str = None
    animator_face_id : int = None
    adjust_c : float = None
    adjust_x : float = None
    adjust_y : float = None
