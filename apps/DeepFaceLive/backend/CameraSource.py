import platform
import time
from datetime import datetime
from enum import IntEnum
from typing import List

import cv2
import numpy as np
from xlib import os as lib_os
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw

from .BackendBase import (BackendConnection, BackendConnectionData, BackendDB,
                          BackendHost, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class CameraSource(BackendHost):
    def __init__(self, weak_heap :  BackendWeakHeap, bc_out : BackendConnection, backend_db : BackendDB = None):
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=CameraSourceWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, bc_out] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

class _ResolutionType(IntEnum):
    RES_320x240 = 0
    RES_640x480 = 1
    RES_720x480 = 2
    RES_1280x720 = 3
    RES_1280x960 = 4
    RES_1366x768 = 5
    RES_1920x1080 = 6

_ResolutionType_names = {_ResolutionType.RES_320x240 : '320x240',
                         _ResolutionType.RES_640x480 : '640x480',
                         _ResolutionType.RES_720x480 : '720x480',
                         _ResolutionType.RES_1280x720 : '1280x720',
                         _ResolutionType.RES_1280x960 : '1280x960',
                         _ResolutionType.RES_1366x768 : '1366x768',
                         _ResolutionType.RES_1920x1080 : '1920x1080',
                        }

_ResolutionType_wh = {_ResolutionType.RES_320x240: (320,240),
                      _ResolutionType.RES_640x480: (640,480),
                      _ResolutionType.RES_720x480: (720,480),
                      _ResolutionType.RES_1280x720: (1280,720),
                      _ResolutionType.RES_1280x960: (1280,960),
                      _ResolutionType.RES_1366x768: (1366,768),
                      _ResolutionType.RES_1920x1080: (1920,1080),
                      }
class _DriverType(IntEnum):
    COMPATIBLE = 0
    DSHOW = 1
    MSMF = 2
    GSTREAMER = 3

_DriverType_names = { _DriverType.COMPATIBLE : 'Compatible',
                      _DriverType.DSHOW : 'DirectShow',
                      _DriverType.MSMF : 'Microsoft Media Foundation',
                      _DriverType.GSTREAMER : 'GStreamer',
                    }

class _RotationType(IntEnum):
    ROTATION_0 = 0
    ROTATION_90 = 1
    ROTATION_180 = 2
    ROTATION_270 = 3

_RotationType_names = ['0 degrees', '90 degrees', '180 degrees', '270 degrees']


class CameraSourceWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, bc_out : BackendConnection):
        self.weak_heap = weak_heap
        self.bc_out = bc_out
        self.bcd_uid = 0
        self.pending_bcd = None
        self.vcap = None
        self.last_timestamp = 0
        lib_os.set_timer_resolution(4)

        state, cs = self.get_state(), self.get_control_sheet()

        cs.driver.call_on_selected(self.on_cs_driver_selected)
        cs.device_idx.call_on_selected(self.on_cs_device_idx_selected)
        cs.resolution.call_on_selected(self.on_cs_resolution_selected)
        cs.fps.call_on_number(self.on_cs_fps)
        cs.rotation.call_on_selected(self.on_cs_rotation_selected)
        cs.flip_horizontal.call_on_flag(self.on_cs_flip_horizontal)
        cs.open_settings.call_on_signal(self.on_cs_open_settings)
        cs.load_settings.call_on_signal(self.on_cs_load_settings)
        cs.save_settings.call_on_signal(self.on_cs_save_settings)

        cs.driver.enable()
        cs.driver.set_choices(_DriverType, _DriverType_names, none_choice_name='@misc.menu_select')
        cs.driver.select(state.driver if state.driver is not None else _DriverType.DSHOW if platform.system() == 'Windows' else _DriverType.COMPATIBLE)

        if platform.system() == 'Windows':
            from xlib.api.win32 import ole32
            from xlib.api.win32 import dshow
            ole32.CoInitializeEx(0,0)
            choices = [ f'{idx} : {name}' for idx, name in enumerate(dshow.get_video_input_devices_names()) ]
            choices += [ f'{idx}' for idx in range(len(choices), 16) ]
            ole32.CoUninitialize()
        else:
            choices = [ f'{idx}' for idx in range(16) ]

        cs.device_idx.enable()
        cs.device_idx.set_choices(choices, none_choice_name='@misc.menu_select')
        cs.device_idx.select(state.device_idx)

        cs.resolution.enable()
        cs.resolution.set_choices(_ResolutionType, _ResolutionType_names, none_choice_name=None)
        cs.resolution.select(state.resolution if state.resolution is not None else _ResolutionType.RES_640x480)

        if state.device_idx is not None and \
           state.driver is not None:

            cv_api = {_DriverType.COMPATIBLE: cv2.CAP_ANY,
                      _DriverType.DSHOW: cv2.CAP_DSHOW,
                      _DriverType.MSMF: cv2.CAP_MSMF,
                      _DriverType.GSTREAMER: cv2.CAP_GSTREAMER,
                      }[state.driver]

            vcap = cv2.VideoCapture(state.device_idx, cv_api)
            if vcap.isOpened():
                self.vcap = vcap
                w, h = _ResolutionType_wh[state.resolution]

                vcap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                vcap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

            if vcap.isOpened():
                cs.fps.enable()
                cs.fps.set_config(lib_csw.Number.Config(min=0, max=240, step=1.0, decimals=2, zero_is_auto=True, allow_instant_update=False))
                cs.fps.set_number(state.fps if state.fps is not None else 0)

                cs.rotation.enable()
                cs.rotation.set_choices(_RotationType, _RotationType_names, none_choice_name=None)
                cs.rotation.select(state.rotation if state.rotation is not None else _RotationType.ROTATION_0)

                cs.flip_horizontal.enable()
                cs.flip_horizontal.set_flag(state.flip_horizontal if state.flip_horizontal is not None else False)

                if platform.system() == 'Windows':
                    cs.open_settings.enable()

                cs.load_settings.enable()
                cs.save_settings.enable()
            else:
                cs.device_idx.unselect()

    def on_cs_driver_selected(self, idx, driver):
        cs, state = self.get_control_sheet(), self.get_state()
        if state.driver != driver:
            state.driver = driver
            self.save_state()
            if self.is_started():
                self.restart()

    def on_cs_device_idx_selected(self, device_idx, device_name):
        cs, state = self.get_control_sheet(), self.get_state()
        if state.device_idx != device_idx:
            state.device_idx = device_idx
            self.save_state()
            if self.is_started():
                self.restart()

    def on_cs_resolution_selected(self, idx, resolution : _ResolutionType):
        state, cs = self.get_state(), self.get_control_sheet()
        if state.resolution != resolution:
            state.resolution = resolution
            self.save_state()
            if self.is_started():
                self.restart()

    def on_cs_fps(self, fps):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.fps.get_config()
        fps = state.fps = np.clip(fps, cfg.min, cfg.max)
        cs.fps.set_number(fps)
        self.save_state()

    def on_cs_rotation_selected(self, idx, _rot_type : _RotationType):
        cs, state = self.get_control_sheet(), self.get_state()
        state.rotation = _rot_type
        self.save_state()

    def on_cs_flip_horizontal(self, flip_horizontal):
        state, cs = self.get_state(), self.get_control_sheet()
        state.flip_horizontal = flip_horizontal
        self.save_state()

    def on_cs_open_settings(self):
        cs, state = self.get_control_sheet(), self.get_state()
        if self.vcap is not None and self.vcap.isOpened():
            self.vcap.set(cv2.CAP_PROP_SETTINGS, 0)

    def on_cs_load_settings(self):
        cs, state = self.get_control_sheet(), self.get_state()

        vcap = self.vcap
        if vcap is not None:
            settings = state.settings_by_idx.get(state.device_idx, None)
            if settings is not None:
                for setting_name, value in settings.items():
                    setting_id = getattr(cv2, setting_name, None)
                    if setting_id is not None:
                        vcap.set(setting_id, value)

    def on_cs_save_settings(self):
        cs, state = self.get_control_sheet(), self.get_state()

        vcap = self.vcap
        if vcap is not None:
            settings = {}
            for setting_name in self._get_vcap_setting_name_list():
                setting_id = getattr(cv2, setting_name, None)
                if setting_id is not None:
                    settings[setting_name] = vcap.get(setting_id)
            state.settings_by_idx[state.device_idx] = settings
            self.save_state()

    def on_tick(self):
        if self.vcap is not None and not self.vcap.isOpened():
            self.set_vcap(None)

        if self.vcap is not None:
            state, cs = self.get_state(), self.get_control_sheet()

            self.start_profile_timing()
            ret, img = self.vcap.read()
            if ret:
                timestamp = datetime.now().timestamp()
                fps = state.fps
                if fps == 0 or ((timestamp - self.last_timestamp) > 1.0 / fps):

                    if fps != 0:
                        if timestamp - self.last_timestamp >= 1.0:
                            self.last_timestamp = timestamp
                        else:
                            self.last_timestamp += 1.0 / fps

                    ip = ImageProcessor(img)
                    ip.ch(3).to_uint8()

                    w, h = _ResolutionType_wh[state.resolution]
                    ip.fit_in(TW=w)

                    rotation = state.rotation
                    if rotation == _RotationType.ROTATION_90:
                        ip.rotate90()
                    elif rotation == _RotationType.ROTATION_180:
                        ip.rotate180()
                    elif rotation == _RotationType.ROTATION_270:
                        ip.rotate270()

                    if state.flip_horizontal:
                        ip.flip_horizontal()

                    img = ip.get_image('HWC')

                    bcd_uid = self.bcd_uid = self.bcd_uid + 1
                    bcd = BackendConnectionData(uid=bcd_uid)

                    bcd.assign_weak_heap(self.weak_heap)
                    frame_name = f'Camera_{state.device_idx}_{bcd_uid:06}'
                    bcd.set_frame_image_name(frame_name)
                    bcd.set_frame_num(bcd_uid)
                    bcd.set_frame_timestamp(timestamp)
                    bcd.set_image(frame_name, img)
                    self.stop_profile_timing()
                    self.pending_bcd = bcd

        if self.pending_bcd is not None:
            if self.bc_out.is_full_read(1):
                self.bc_out.write(self.pending_bcd)
                self.pending_bcd = None

        time.sleep(0.001)

    def set_vcap(self, vcap):
        if self.vcap is not None:
            if self.vcap.isOpened():
                self.vcap.release()
            self.vcap = None
        self.vcap = vcap

    def on_stop(self):
        if self.vcap is not None:
            if self.vcap.isOpened():
                self.vcap.release()
            self.vcap = None

    def _get_vcap_setting_name_list(self) -> List[str]:
        return ['CAP_PROP_BRIGHTNESS',
                'CAP_PROP_CONTRAST',
                'CAP_PROP_SATURATION',
                'CAP_PROP_HUE',
                'CAP_PROP_SHARPNESS',
                'CAP_PROP_GAMMA',
                'CAP_PROP_AUTO_WB',
                'CAP_PROP_XI_AUTO_WB',
                'CAP_PROP_XI_MANUAL_WB',
                'CAP_PROP_WB_TEMPERATURE',
                'CAP_PROP_BACKLIGHT',
                'CAP_PROP_GAIN',
                'CAP_PROP_AUTO_EXPOSURE',
                'CAP_PROP_EXPOSURE']

class WorkerState(BackendWorkerState):
    def __init__(self):
        self.device_idx : int = None
        self.driver : _DriverType = None
        self.resolution : _ResolutionType = None
        self.fps : float = None
        self.rotation : _RotationType = None
        self.flip_horizontal : bool = None
        self.settings_by_idx = {}

class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.device_idx = lib_csw.DynamicSingleSwitch.Client()
            self.driver = lib_csw.DynamicSingleSwitch.Client()
            self.resolution = lib_csw.DynamicSingleSwitch.Client()
            self.fps = lib_csw.Number.Client()
            self.rotation = lib_csw.DynamicSingleSwitch.Client()
            self.flip_horizontal = lib_csw.Flag.Client()
            self.open_settings = lib_csw.Signal.Client()
            self.save_settings = lib_csw.Signal.Client()
            self.load_settings = lib_csw.Signal.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.device_idx = lib_csw.DynamicSingleSwitch.Host()
            self.driver = lib_csw.DynamicSingleSwitch.Host()
            self.resolution = lib_csw.DynamicSingleSwitch.Host()
            self.fps = lib_csw.Number.Host()
            self.rotation = lib_csw.DynamicSingleSwitch.Host()
            self.flip_horizontal = lib_csw.Flag.Host()
            self.open_settings = lib_csw.Signal.Host()
            self.save_settings = lib_csw.Signal.Host()
            self.load_settings = lib_csw.Signal.Host()
