import time

import numpy as np
from xlib import os as lib_os
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class FrameAdjuster(BackendHost):

    def __init__(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out  : BackendConnection, backend_db : BackendDB = None):
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FrameAdjusterWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out] )

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

class FrameAdjusterWorker(BackendWorker):
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
        cs.median_blur_per.call_on_number(self.on_cs_median_blur_per)
        cs.degrade_bicubic_per.call_on_number(self.on_cs_degrade_bicubic_per)

        cs.median_blur_per.enable()
        cs.median_blur_per.set_config(lib_csw.Number.Config(min=0, max=100, step=1, decimals=0, allow_instant_update=True))
        cs.median_blur_per.set_number(state.median_blur_per if state.median_blur_per is not None else 0)

        cs.degrade_bicubic_per.enable()
        cs.degrade_bicubic_per.set_config(lib_csw.Number.Config(min=0, max=100, step=1, decimals=0, allow_instant_update=True))
        cs.degrade_bicubic_per.set_number(state.degrade_bicubic_per if state.degrade_bicubic_per is not None else 0)

    def on_cs_median_blur_per(self, median_blur_per):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.median_blur_per.get_config()
        median_blur_per = state.median_blur_per = int(np.clip(median_blur_per, cfg.min, cfg.max))
        cs.median_blur_per.set_number(median_blur_per)
        self.save_state()
        self.reemit_frame_signal.send()

    def on_cs_degrade_bicubic_per(self, degrade_bicubic_per):
        state, cs = self.get_state(), self.get_control_sheet()
        cfg = cs.degrade_bicubic_per.get_config()
        degrade_bicubic_per = state.degrade_bicubic_per = int(np.clip(degrade_bicubic_per, cfg.min, cfg.max))
        cs.degrade_bicubic_per.set_number(degrade_bicubic_per)
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

                if frame_image is not None:
                    frame_image_ip = ImageProcessor(frame_image)
                    frame_image_ip.median_blur(5, opacity=state.median_blur_per / 100.0 )
                    frame_image_ip.reresize( state.degrade_bicubic_per / 100.0, interpolation=ImageProcessor.Interpolation.CUBIC)

                    frame_image = frame_image_ip.get_image('HWC')
                    bcd.set_image(frame_image_name, frame_image)

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
            self.median_blur_per = lib_csw.Number.Client()
            self.degrade_bicubic_per = lib_csw.Number.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.median_blur_per = lib_csw.Number.Host()
            self.degrade_bicubic_per = lib_csw.Number.Host()

class WorkerState(BackendWorkerState):
    median_blur_per : int = None
    degrade_bicubic_per : int = None
