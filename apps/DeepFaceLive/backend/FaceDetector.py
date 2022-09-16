import time
from enum import IntEnum

import numpy as np
from modelhub import onnx as onnx_models
from xlib import os as lib_os
from xlib.face import FRect
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState, BackendFaceSwapInfo)


class DetectorType(IntEnum):
    CENTER_FACE = 0
    S3FD = 1
    YOLOV5 = 2

DetectorTypeNames = ['CenterFace', 'S3FD', 'YoloV5']

class FaceSortBy(IntEnum):
    LARGEST = 0
    DIST_FROM_CENTER = 1
    LEFT_RIGHT = 2
    RIGHT_LEFT = 3
    TOP_BOTTOM = 4
    BOTTOM_TOP = 5

FaceSortByNames = ['@FaceDetector.LARGEST', '@FaceDetector.DIST_FROM_CENTER',
                   '@FaceDetector.LEFT_RIGHT', '@FaceDetector.RIGHT_LEFT',
                   '@FaceDetector.TOP_BOTTOM', '@FaceDetector.BOTTOM_TOP' ]

class FaceDetector(BackendHost):
    def __init__(self,  weak_heap :  BackendWeakHeap,
                        reemit_frame_signal : BackendSignal,
                        bc_in : BackendConnection,
                        bc_out : BackendConnection,
                        backend_db : BackendDB = None):
        self._weak_heap = weak_heap
        self._bc_out = bc_out
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceDetectorWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

    def get_weak_heap(self) -> BackendWeakHeap: return self._weak_heap
    def get_bc_out(self) -> BackendConnection: return self._bc_out

class FaceDetectorWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal,
                       bc_in : BackendConnection,
                       bc_out : BackendConnection):

        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.pending_bcd = None

        self.temporal_rects = []
        self.CenterFace = None
        self.S3FD = None
        self.YoloV5Face = None

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()
        cs.detector_type.call_on_selected(self.on_cs_detector_type)
        cs.device.call_on_selected(self.on_cs_devices)
        cs.fixed_window_size.call_on_number(self.on_cs_fixed_window_size)
        cs.threshold.call_on_number(self.on_cs_threshold)
        cs.max_faces.call_on_number(self.on_cs_max_faces)
        cs.sort_by.call_on_selected(self.on_cs_sort_by)
        cs.temporal_smoothing.call_on_number(self.on_cs_temporal_smoothing)

        cs.detector_type.enable()
        cs.detector_type.set_choices(DetectorType, DetectorTypeNames, none_choice_name=None)
        cs.detector_type.select(state.detector_type if state.detector_type is not None else DetectorType.YOLOV5)


    def on_cs_detector_type(self, idx, detector_type):
        state, cs = self.get_state(), self.get_control_sheet()

        if state.detector_type == detector_type:
            if detector_type == DetectorType.CENTER_FACE:
                cs.device.enable()
                cs.device.set_choices( onnx_models.CenterFace.get_available_devices(), none_choice_name='@misc.menu_select')
                cs.device.select(state.center_face_state.device)
            elif detector_type == DetectorType.S3FD:
                cs.device.enable()
                cs.device.set_choices (onnx_models.S3FD.get_available_devices(), none_choice_name='@misc.menu_select')
                cs.device.select(state.S3FD_state.device)
            elif detector_type == DetectorType.YOLOV5:
                cs.device.enable()
                cs.device.set_choices (onnx_models.YoloV5Face.get_available_devices(), none_choice_name='@misc.menu_select')
                cs.device.select(state.YoloV5_state.device)
        else:
            state.detector_type = detector_type
            self.save_state()
            self.restart()



    def on_cs_devices(self, idx, device):
        state, cs = self.get_state(), self.get_control_sheet()
        detector_type = state.detector_type

        if device is not None and \
           (detector_type == DetectorType.CENTER_FACE and state.center_face_state.device == device) or \
           (detector_type == DetectorType.S3FD and state.S3FD_state.device == device) or \
           (detector_type == DetectorType.YOLOV5 and state.YoloV5_state.device == device):

            detector_state = state.get_detector_state()

            cs.max_faces.enable()
            cs.max_faces.set_config(lib_csw.Number.Config(min=0, max=256, step=1, decimals=0, allow_instant_update=True))
            cs.max_faces.set_number(detector_state.max_faces or 1)

            if detector_type in [DetectorType.CENTER_FACE, DetectorType.S3FD, DetectorType.YOLOV5]:
                cs.fixed_window_size.enable()
                cs.fixed_window_size.set_config(lib_csw.Number.Config(min=0, max=4096, step=32, decimals=0, zero_is_auto=True, allow_instant_update=True))
                cs.fixed_window_size.set_number(detector_state.fixed_window_size if detector_state.fixed_window_size is not None else 480)

                cs.threshold.enable()
                cs.threshold.set_config(lib_csw.Number.Config(min=0.01, max=1.0, step=0.01, decimals=2, allow_instant_update=True))
                cs.threshold.set_number(detector_state.threshold if detector_state.threshold is not None else 0.5)

                cs.sort_by.enable()
                cs.sort_by.set_choices(FaceSortBy, FaceSortByNames)
                cs.sort_by.select(detector_state.sort_by if detector_state.sort_by is not None else FaceSortBy.LARGEST)

                cs.temporal_smoothing.enable()
                cs.temporal_smoothing.set_config(lib_csw.Number.Config(min=1, max=150, step=1, allow_instant_update=True))
                cs.temporal_smoothing.set_number(detector_state.temporal_smoothing if detector_state.temporal_smoothing is not None else 1)

            if detector_type == DetectorType.CENTER_FACE:
                self.CenterFace = onnx_models.CenterFace(device)
            elif detector_type == DetectorType.S3FD:
                self.S3FD = onnx_models.S3FD(device)
            elif detector_type == DetectorType.YOLOV5:
                self.YoloV5Face = onnx_models.YoloV5Face(device)
        else:
            if detector_type == DetectorType.CENTER_FACE:
                state.center_face_state.device = device
            elif detector_type == DetectorType.S3FD:
                state.S3FD_state.device = device
            elif detector_type == DetectorType.YOLOV5:
                state.YoloV5_state.device = device

            self.save_state()
            self.restart()


    def on_cs_fixed_window_size(self, fixed_window_size):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.fixed_window_size.get_config()
        fixed_window_size = state.get_detector_state().fixed_window_size = int(np.clip(fixed_window_size, cfg.min, cfg.max))
        cs.fixed_window_size.set_number(fixed_window_size)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_threshold(self, threshold):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.threshold.get_config()
        threshold = state.get_detector_state().threshold = np.clip(threshold, cfg.min, cfg.max)
        cs.threshold.set_number(threshold)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_max_faces(self, max_faces):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.max_faces.get_config()
        max_faces = state.get_detector_state().max_faces = np.clip(max_faces, cfg.min, cfg.max)
        cs.max_faces.set_number(max_faces)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_sort_by(self, idx, sort_by):
        state, cs = self.get_state(), self.get_control_sheet()
        state.get_detector_state().sort_by = sort_by
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_temporal_smoothing(self, temporal_smoothing):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.temporal_smoothing.get_config()
        temporal_smoothing = state.get_detector_state().temporal_smoothing = int(np.clip(temporal_smoothing, cfg.min, cfg.max))
        if temporal_smoothing == 1:
            self.temporal_rects = []
        cs.temporal_smoothing.set_number(temporal_smoothing)
        self.save_state()
        self.reemit_frame_signal.send()


    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)
                is_frame_reemitted = bcd.get_is_frame_reemitted()

                detector_type = state.detector_type
                if (detector_type == DetectorType.CENTER_FACE and self.CenterFace is not None) or \
                    (detector_type == DetectorType.S3FD and self.S3FD is not None) or \
                    (detector_type == DetectorType.YOLOV5 and self.YoloV5Face is not None):

                    detector_state = state.get_detector_state()

                    frame_image_name = bcd.get_frame_image_name()
                    frame_image = bcd.get_image(frame_image_name)

                    if frame_image is not None:
                        _,H,W,_ = ImageProcessor(frame_image).get_dims()

                        rects = []
                        if detector_type == DetectorType.CENTER_FACE:
                            rects = self.CenterFace.extract (frame_image, threshold=detector_state.threshold, fixed_window=detector_state.fixed_window_size)[0]
                        elif detector_type == DetectorType.S3FD:
                            rects = self.S3FD.extract (frame_image, threshold=detector_state.threshold, fixed_window=detector_state.fixed_window_size)[0]
                        elif detector_type == DetectorType.YOLOV5:
                            rects = self.YoloV5Face.extract (frame_image, threshold=detector_state.threshold, fixed_window=detector_state.fixed_window_size)[0]

                        # to list of FaceURect
                        rects = [ FRect.from_ltrb( (l/W, t/H, r/W, b/H) ) for l,t,r,b in rects ]

                        # sort
                        if detector_state.sort_by == FaceSortBy.LARGEST:
                            rects = FRect.sort_by_area_size(rects)
                        elif detector_state.sort_by == FaceSortBy.DIST_FROM_CENTER:
                            rects = FRect.sort_by_dist_from_2D_point(rects, 0.5, 0.5)
                        elif detector_state.sort_by == FaceSortBy.LEFT_RIGHT:
                            rects = FRect.sort_by_dist_from_horizontal_point(rects, 0)
                        elif detector_state.sort_by == FaceSortBy.RIGHT_LEFT:
                            rects = FRect.sort_by_dist_from_horizontal_point(rects, 1)
                        elif detector_state.sort_by == FaceSortBy.TOP_BOTTOM:
                            rects = FRect.sort_by_dist_from_vertical_point(rects, 0)
                        elif detector_state.sort_by == FaceSortBy.BOTTOM_TOP:
                            rects = FRect.sort_by_dist_from_vertical_point(rects, 1)

                        if len(rects) != 0:
                            max_faces = detector_state.max_faces
                            if max_faces != 0 and len(rects) > max_faces:
                                rects = rects[:max_faces]

                            if detector_state.temporal_smoothing != 1:
                                if len(self.temporal_rects) != len(rects):
                                    self.temporal_rects = [ [] for _ in range(len(rects)) ]

                            for face_id, face_urect in enumerate(rects):
                                if detector_state.temporal_smoothing != 1:
                                    if not is_frame_reemitted or len(self.temporal_rects[face_id]) == 0:
                                        self.temporal_rects[face_id].append( face_urect.as_4pts() )

                                    self.temporal_rects[face_id] = self.temporal_rects[face_id][-detector_state.temporal_smoothing:]

                                    face_urect = FRect.from_4pts ( np.mean(self.temporal_rects[face_id],0 ) )

                                if face_urect.get_area() != 0:
                                    fsi = BackendFaceSwapInfo()
                                    fsi.image_name = frame_image_name
                                    fsi.face_urect = face_urect
                                    bcd.add_face_swap_info(fsi)

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
            self.detector_type = lib_csw.DynamicSingleSwitch.Client()
            self.device = lib_csw.DynamicSingleSwitch.Client()
            self.sort_by = lib_csw.DynamicSingleSwitch.Client()
            self.fixed_window_size = lib_csw.Number.Client()
            self.threshold = lib_csw.Number.Client()
            self.max_faces = lib_csw.Number.Client()
            self.temporal_smoothing = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.detector_type = lib_csw.DynamicSingleSwitch.Host()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.sort_by = lib_csw.DynamicSingleSwitch.Host()
            self.fixed_window_size = lib_csw.Number.Host()
            self.threshold = lib_csw.Number.Host()
            self.max_faces = lib_csw.Number.Host()
            self.temporal_smoothing = lib_csw.Number.Host()

class DetectorState(BackendWorkerState):
    fixed_window_size : int = None
    threshold : float = None
    max_faces : int = None
    sort_by : FaceSortBy = None
    temporal_smoothing : int = None

class CenterFaceState(BackendWorkerState):
    device = None

class S3FDState(BackendWorkerState):
    device = None

class YoloV5FaceState(BackendWorkerState):
    device = None

class WorkerState(BackendWorkerState):
    def __init__(self):
        self.detector_type : DetectorType = None
        self.detector_state = {}
        self.center_face_state = CenterFaceState()
        self.S3FD_state = S3FDState()
        self.YoloV5_state = YoloV5FaceState()

    def get_detector_state(self) -> DetectorState:
        state = self.detector_state.get(self.detector_type, None)
        if state is None:
            state = self.detector_state[self.detector_type] = DetectorState()
        return state
