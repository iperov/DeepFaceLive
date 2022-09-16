import time
from enum import IntEnum
import numpy as np
from modelhub import onnx as onnx_models
from modelhub import cv as cv_models

from xlib import os as lib_os
from xlib.face import ELandmarks2D, FLandmarks2D, FPose
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)

class MarkerType(IntEnum):
    OPENCV_LBF = 0
    GOOGLE_FACEMESH = 1
    INSIGHT_2D106 = 2

MarkerTypeNames = ['OpenCV LBF','Google FaceMesh','InsightFace_2D106']

class FaceMarker(BackendHost):
    def __init__(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, backend_db : BackendDB = None):

        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceMarkerWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out, ] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()


class FaceMarkerWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal,
                       bc_in : BackendConnection,
                       bc_out : BackendConnection,
                       ):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.pending_bcd = None
        self.opencv_lbf = None
        self.google_facemesh = None
        self.insightface_2d106 = None
        self.temporal_lmrks = []

        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()
        cs.marker_type.call_on_selected(self.on_cs_marker_type)
        cs.device.call_on_selected(self.on_cs_devices)
        cs.marker_coverage.call_on_number(self.on_cs_marker_coverage)
        cs.temporal_smoothing.call_on_number(self.on_cs_temporal_smoothing)

        cs.marker_type.enable()
        cs.marker_type.set_choices(MarkerType, MarkerTypeNames, none_choice_name=None)
        cs.marker_type.select(state.marker_type if state.marker_type is not None else MarkerType.GOOGLE_FACEMESH)

    def on_cs_marker_type(self, idx, marker_type):
        state, cs = self.get_state(), self.get_control_sheet()

        if state.marker_type == marker_type:
            cs.device.enable()
            if marker_type == MarkerType.OPENCV_LBF:
                cs.device.set_choices(['CPU'], none_choice_name='@misc.menu_select')
                cs.device.select(state.opencv_lbf_state.device)
            elif marker_type == MarkerType.GOOGLE_FACEMESH:
                cs.device.set_choices(onnx_models.FaceMesh.get_available_devices(), none_choice_name='@misc.menu_select')
                cs.device.select(state.google_facemesh_state.device)
            elif marker_type == MarkerType.INSIGHT_2D106:
                cs.device.set_choices(onnx_models.InsightFace2D106.get_available_devices(), none_choice_name='@misc.menu_select')
                cs.device.select(state.insightface_2d106_state.device)

        else:
            state.marker_type = marker_type
            self.save_state()
            self.restart()

    def on_cs_devices(self, idx, device):
        state, cs = self.get_state(), self.get_control_sheet()
        marker_type = state.marker_type

        if device is not None and \
            ( (marker_type == MarkerType.OPENCV_LBF and state.opencv_lbf_state.device == device) or \
              (marker_type == MarkerType.GOOGLE_FACEMESH and state.google_facemesh_state.device == device) or \
              (marker_type == MarkerType.INSIGHT_2D106 and state.insightface_2d106_state.device == device) ):
            marker_state = state.get_marker_state()

            if state.marker_type == MarkerType.OPENCV_LBF:
                self.opencv_lbf = cv_models.FaceMarkerLBF()
            elif state.marker_type == MarkerType.GOOGLE_FACEMESH:
                self.google_facemesh = onnx_models.FaceMesh(state.google_facemesh_state.device)
            elif state.marker_type == MarkerType.INSIGHT_2D106:
                self.insightface_2d106 = onnx_models.InsightFace2D106(state.insightface_2d106_state.device)

            cs.marker_coverage.enable()
            cs.marker_coverage.set_config(lib_csw.Number.Config(min=0.1, max=3.0, step=0.1, decimals=1, allow_instant_update=True))

            marker_coverage = marker_state.marker_coverage
            if marker_coverage is None:
                if marker_type == MarkerType.OPENCV_LBF:
                    marker_coverage = 1.1
                elif marker_type == MarkerType.GOOGLE_FACEMESH:
                    marker_coverage = 1.4
                elif marker_type == MarkerType.INSIGHT_2D106:
                    marker_coverage = 1.6
            cs.marker_coverage.set_number(marker_coverage)

            cs.temporal_smoothing.enable()
            cs.temporal_smoothing.set_config(lib_csw.Number.Config(min=1, max=150, step=1, allow_instant_update=True))
            cs.temporal_smoothing.set_number(marker_state.temporal_smoothing if marker_state.temporal_smoothing is not None else 1)

        else:
            if marker_type == MarkerType.OPENCV_LBF:
                state.opencv_lbf_state.device = device
            elif marker_type == MarkerType.GOOGLE_FACEMESH:
                state.google_facemesh_state.device = device
            elif marker_type == MarkerType.INSIGHT_2D106:
                state.insightface_2d106_state.device = device
            self.save_state()
            self.restart()


    def on_cs_marker_coverage(self, marker_coverage):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.marker_coverage.get_config()
        marker_coverage = state.get_marker_state().marker_coverage = np.clip(marker_coverage, cfg.min, cfg.max)
        cs.marker_coverage.set_number(marker_coverage)
        self.save_state()
        self.reemit_frame_signal.send()


    def on_cs_temporal_smoothing(self, temporal_smoothing):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.temporal_smoothing.get_config()
        temporal_smoothing = state.get_marker_state().temporal_smoothing = int(np.clip(temporal_smoothing,  cfg.min, cfg.max))
        if temporal_smoothing == 1:
            self.temporal_lmrks = []
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

                marker_type = state.marker_type
                marker_state = state.get_marker_state()

                is_opencv_lbf = marker_type == MarkerType.OPENCV_LBF and self.opencv_lbf is not None
                is_google_facemesh = marker_type == MarkerType.GOOGLE_FACEMESH and self.google_facemesh is not None
                is_insightface_2d106 = marker_type == MarkerType.INSIGHT_2D106 and self.insightface_2d106 is not None
                is_marker_loaded = is_opencv_lbf or is_google_facemesh or is_insightface_2d106

                if marker_type is not None:
                    frame_image = bcd.get_image(bcd.get_frame_image_name())

                    if frame_image is not None and is_marker_loaded:
                        fsi_list = bcd.get_face_swap_info_list()
                        if marker_state.temporal_smoothing != 1 and \
                            len(self.temporal_lmrks) != len(fsi_list):
                            self.temporal_lmrks = [ [] for _ in range(len(fsi_list)) ]

                        for face_id, fsi in enumerate(fsi_list):
                            if fsi.face_urect is not None:
                                # Cut the face to feed to the face marker
                                face_image, face_uni_mat = fsi.face_urect.cut(frame_image, marker_state.marker_coverage, 256 if is_opencv_lbf else \
                                                                                                                         192 if is_google_facemesh else \
                                                                                                                         192 if is_insightface_2d106 else 0 )
                                _,H,W,_ = ImageProcessor(face_image).get_dims()
                                if is_opencv_lbf:
                                    lmrks = self.opencv_lbf.extract(face_image)[0]
                                elif is_google_facemesh:
                                    lmrks = self.google_facemesh.extract(face_image)[0]
                                elif is_insightface_2d106:
                                    lmrks = self.insightface_2d106.extract(face_image)[0]

                                if marker_state.temporal_smoothing != 1:
                                    if not is_frame_reemitted or len(self.temporal_lmrks[face_id]) == 0:
                                        self.temporal_lmrks[face_id].append(lmrks)
                                    self.temporal_lmrks[face_id] = self.temporal_lmrks[face_id][-marker_state.temporal_smoothing:]
                                    lmrks = np.mean(self.temporal_lmrks[face_id],0 )

                                if is_google_facemesh:
                                    fsi.face_pose = FPose.from_3D_468_landmarks(lmrks)

                                if is_opencv_lbf:
                                    lmrks /= (W,H)
                                elif is_google_facemesh:
                                    lmrks = lmrks[...,0:2] / (W,H)
                                elif is_insightface_2d106:
                                    lmrks = lmrks[...,0:2] / (W,H)

                                face_ulmrks = FLandmarks2D.create (ELandmarks2D.L68 if is_opencv_lbf else \
                                                                   ELandmarks2D.L468 if is_google_facemesh else \
                                                                   ELandmarks2D.L106 if is_insightface_2d106 else None, lmrks)
                                face_ulmrks = face_ulmrks.transform(face_uni_mat, invert=True)
                                fsi.face_ulmrks = face_ulmrks

                    self.stop_profile_timing()
                self.pending_bcd = bcd

        if self.pending_bcd is not None:
            if self.bc_out.is_full_read(1):
                self.bc_out.write(self.pending_bcd)
                self.pending_bcd = None
            else:
                time.sleep(0.001)

class MarkerState(BackendWorkerState):
    marker_coverage : float = None
    temporal_smoothing : int = None

class OpenCVLBFState(BackendWorkerState):
    device = None

class GoogleFaceMeshState(BackendWorkerState):
    device = None

class Insight2D106State(BackendWorkerState):
    device = None

class WorkerState(BackendWorkerState):
    def __init__(self):
        self.marker_type : MarkerType = None
        self.marker_state = {}
        self.opencv_lbf_state = OpenCVLBFState()
        self.google_facemesh_state = GoogleFaceMeshState()
        self.insightface_2d106_state = Insight2D106State()

    def get_marker_state(self) -> MarkerState:
        state = self.marker_state.get(self.marker_type, None)
        if state is None:
            state = self.marker_state[self.marker_type] = MarkerState()
        return state

class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.marker_type = lib_csw.DynamicSingleSwitch.Client()
            self.device = lib_csw.DynamicSingleSwitch.Client()
            self.marker_coverage = lib_csw.Number.Client()
            self.temporal_smoothing = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.marker_type = lib_csw.DynamicSingleSwitch.Host()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.marker_coverage = lib_csw.Number.Host()
            self.temporal_smoothing = lib_csw.Number.Host()

# lmrks_list = []

# offsets = [ (0,0), (-2,0), (0,-2), (2,0), (0,2) ]

# for x_off, y_off in offsets:
#     feed_image = face_image.copy()

#     if x_off > 0:
#         feed_image[:-x_off] = feed_image[x_off:]
#     elif x_off < 0:
#         feed_image[x_off:] = feed_image[:-x_off]

#     if y_off > 0:
#         feed_image[:,:-y_off] = feed_image[:,y_off:]
#     elif y_off < 0:
#         feed_image[:,y_off:] = feed_image[:,:-y_off]

#     if marker_type == MarkerType.OPENCV_LBF:
#         lmrks = self.opencv_lbf.extract(feed_image)

#     lmrks_list.append(lmrks)

# #print(lmrks_list)
# lmrks = np.mean(lmrks_list, 0)
# self.temporal_lmrks.append(lmrks)
# if len(self.temporal_lmrks) >= 5:
#     self.temporal_lmrks.pop(0)
# lmrks = np.mean(self.temporal_lmrks,0 )



# x = 4
# spatial_offsets = [ (0,0), (-x,0), (0,-x), (x,0), (0,x) ]

# lmrks_list = []
# for i in range(temporal_smoothing):
#     if temporal_smoothing == 1:
#         feed_image = face_image
#     else:
#         feed_image = face_image.copy()

#         x_off,y_off = spatial_offsets[i]

#         if x_off > 0:
#             feed_image[:-x_off] = feed_image[x_off:]
#         elif x_off < 0:
#             feed_image[x_off:] = feed_image[:-x_off]

#         if y_off > 0:
#             feed_image[:,:-y_off] = feed_image[:,y_off:]
#         elif y_off < 0:
#             feed_image[:,y_off:] = feed_image[:,:-y_off]


#     lmrks_list.append(lmrks)

# lmrks = np.mean(lmrks_list, 0)
