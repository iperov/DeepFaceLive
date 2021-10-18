import time
from enum import IntEnum
from pathlib import Path

from xlib import os as lib_os
from xlib import player as lib_player
from xlib.image import ImageProcessor
from xlib.mp import csw as lib_csw

from .BackendBase import (BackendConnection, BackendConnectionData, BackendDB,
                          BackendHost, BackendSignal, BackendWeakHeap,
                          BackendWorker, BackendWorkerState)


class InputType(IntEnum):
    IMAGE_SEQUENCE = 0
    VIDEO_FILE = 1

InputTypeNames = ['@FileSource.image_folder', '@FileSource.video_file']

class FileSource(BackendHost):
    def __init__(self,  weak_heap : BackendWeakHeap,
                        reemit_frame_signal : BackendSignal,
                        bc_out : BackendConnection, backend_db : BackendDB = None):
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FileSourceWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_out])

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()


class FileSourceWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_out : BackendConnection):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_out = bc_out
        self.bcd_uid = 0
        self.pending_bcd = None
        self.fp : lib_player.FramePlayer = None
        self.last_p_frame = None
        lib_os.set_timer_resolution(4)

        state, cs = self.get_state(), self.get_control_sheet()

        cs.input_type.call_on_selected(self.on_cs_input_type_selected)
        cs.input_paths.call_on_paths(self.on_cs_input_paths)
        cs.target_width.call_on_number(self.on_cs_target_width)
        cs.fps.call_on_number(self.on_cs_fps)
        cs.is_realtime.call_on_flag(self.on_cs_is_realtime)
        cs.is_autorewind.call_on_flag(self.on_cs_is_autorewind)
        cs.frame_index.call_on_number(self.on_cs_frame_index)

        cs.play.call_on_signal(self.on_cs_play)
        cs.pause.call_on_signal(self.on_cs_pause)
        cs.seek_begin.call_on_signal(self.on_cs_seek_begin)
        cs.seek_backward.call_on_signal(self.on_cs_seek_backward)
        cs.seek_forward.call_on_signal(self.on_cs_seek_forward)
        cs.seek_end.call_on_signal(self.on_cs_seek_end)

        cs.input_type.enable()
        cs.input_type.set_choices(InputType, InputTypeNames)
        cs.input_type.select(state.input_type)



    def set_fp(self, fp):
        if self.fp != fp:
            if self.fp is not None:
                self.fp.dispose()
            self.fp = fp

    #######################
    ### messages
    def on_cs_input_type_selected(self, idx, input_type):
        cs, state = self.get_control_sheet(), self.get_state()
        cs.input_paths.disable()
        cs.target_width.disable()
        cs.fps.disable()
        cs.is_autorewind.disable()
        cs.is_realtime.disable()
        cs.frame_index.disable()
        cs.frame_count.disable()
        cs.play.disable()
        cs.pause.disable()
        cs.seek_backward.disable()
        cs.seek_forward.disable()
        cs.seek_begin.disable()
        cs.seek_end.disable()

        self.set_fp(None)

        if input_type is not None:
            cs.input_paths.enable()
            if input_type == InputType.IMAGE_SEQUENCE:
                cs.input_paths.set_config( lib_csw.Paths.Config.Directory() )
            elif input_type == InputType.VIDEO_FILE:
                cs.input_paths.set_config( lib_csw.Paths.Config.ExistingFile(caption='Video file', suffixes=lib_player.VideoFilePlayer.SUPPORTED_VIDEO_FILE_SUFFIXES ) )

        if input_type == state.input_type:
            cs.input_paths.set_paths(state.input_path)
        else:
            state.input_type = input_type
            state.input_path = None
            cs.input_paths.set_paths(None)
            state.fp_state = None
            self.save_state()

    def on_cs_input_paths(self, paths, prev_paths):
        state, cs = self.get_state(), self.get_control_sheet()
        cs.error.set_error(None)

        input_type = state.input_type
        input_path = paths[0] if len(paths) != 0 else None

        if input_path is not None:
            if  input_type == InputType.IMAGE_SEQUENCE or \
                input_type == InputType.VIDEO_FILE:

                cls_ = lib_player.ImageSequencePlayer if input_type == InputType.IMAGE_SEQUENCE \
                        else lib_player.VideoFilePlayer

                err = None
                try:
                    fp = cls_(input_path)
                except Exception as e:
                    err = str(e)

                if err is None:
                    self.set_fp(fp)
                    fp.req_frame_seek(0, 0)

                    if input_path == state.input_path and state.fp_state is not None:
                        target_width  = fp.set_target_width(state.fp_state.target_width)
                        fps           = fp.set_fps(state.fp_state.fps)
                        is_realtime   = fp.set_is_realtime(state.fp_state.is_realtime)
                        is_autorewind = fp.set_is_autorewind(state.fp_state.is_autorewind)
                    else:
                        state.input_path = input_path
                        state.fp_state = FPState()
                        target_width  = state.fp_state.target_width  = fp.get_target_width()
                        fps           = state.fp_state.fps           = fp.get_fps()
                        is_realtime   = state.fp_state.is_realtime   = fp.set_is_realtime(True)
                        is_autorewind = state.fp_state.is_autorewind = fp.set_is_autorewind(True)

                    cs.target_width.enable()
                    cs.target_width.set_config(lib_csw.Number.Config(min=0, max=4096, step=4, decimals=0, zero_is_auto=True, allow_instant_update=True))
                    cs.target_width.set_number(target_width)

                    cs.fps.enable()
                    cs.fps.set_config(lib_csw.Number.Config(min=0, max=240, step=1.0, decimals=2, zero_is_auto=True, allow_instant_update=True))
                    cs.fps.set_number(fps)

                    cs.is_realtime.enable()
                    cs.is_realtime.set_flag(is_realtime)

                    cs.is_autorewind.enable()
                    cs.is_autorewind.set_flag(is_autorewind)

                    cs.frame_count.enable()
                    cs.frame_count.set_number( fp.get_frame_count() )

                    cs.frame_index.enable()
                    cs.frame_index.set_number( fp.get_frame_idx() )

                    cs.play.enable()
                    cs.pause.freeze()
                    cs.seek_backward.enable()
                    cs.seek_forward.enable()
                    cs.seek_begin.enable()
                    cs.seek_end.enable()
                else:
                    cs.error.set_error(err)
                    cs.input_paths.set_paths(prev_paths, block_event=True)
        self.save_state()


    def on_cs_target_width(self, target_width):
        state, cs = self.get_state(), self.get_control_sheet()
        target_width = state.fp_state.target_width = self.fp.set_target_width(target_width)
        cs.target_width.set_number(target_width)
        self.save_state()

    def on_cs_fps(self, fps):
        state, cs = self.get_state(), self.get_control_sheet()
        fps = state.fp_state.fps = self.fp.set_fps(fps)
        cs.fps.set_number(fps)
        self.save_state()

    def on_cs_is_realtime(self, is_realtime):
        state, cs = self.get_state(), self.get_control_sheet()
        is_realtime = state.fp_state.is_realtime = self.fp.set_is_realtime(is_realtime)
        cs.is_realtime.set_flag(is_realtime)
        if not cs.is_realtime.get_flag():
            cs.fps.freeze()
        else:
            cs.fps.enable()
        self.save_state()

    def on_cs_is_autorewind(self, is_autorewind):
        state, cs = self.get_state(), self.get_control_sheet()
        is_autorewind = state.fp_state.is_autorewind = self.fp.set_is_autorewind(is_autorewind)
        cs.is_autorewind.set_flag(is_autorewind)
        self.save_state()

    def on_cs_play(self):
        self.fp.req_play_start()

    def on_cs_pause(self):
        self.fp.req_play_stop()

    def on_cs_seek_begin(self):
        self.fp.req_frame_seek(0,0)

    def on_cs_seek_backward(self):
        self.fp.req_frame_seek(-1,1)

    def on_cs_seek_forward(self):
        self.fp.req_frame_seek(1,1)

    def on_cs_seek_end(self):
        self.fp.req_frame_seek(0,2)

    def on_cs_frame_index(self, frame_idx):
        self.fp.req_frame_seek(frame_idx, 0)

    def on_fp_state_change(self, fp, is_playing):
        state, cs = self.get_state(), self.get_control_sheet()

        if is_playing:
            cs.play.freeze()
            cs.pause.enable()
            cs.seek_backward.freeze()
            cs.seek_forward.freeze()
        else:
            cs.play.enable()
            cs.pause.freeze()
            cs.seek_backward.enable()
            cs.seek_forward.enable()

    def on_tick(self):
        if self.fp is not None:
            state, cs = self.get_state(), self.get_control_sheet()

            if state.fp_state.is_realtime or self.pending_bcd is None:
                self.start_profile_timing()
                reemit_frame = self.reemit_frame_signal.recv()

                pr = self.fp.process()
                if pr.new_is_playing is not None:
                    if pr.new_is_playing:
                        cs.play.freeze()
                        cs.pause.enable()
                        cs.seek_backward.freeze()
                        cs.seek_forward.freeze()
                    else:
                        cs.play.enable()
                        cs.pause.freeze()
                        cs.seek_backward.enable()
                        cs.seek_forward.enable()

                if pr.new_error is not None:
                    cs.error.set_error(pr.new_error)

                if pr.new_frame_idx is not None:
                    cs.frame_index.set_number(pr.new_frame_idx, block_event=True)

                p_frame = pr.new_frame
                if p_frame is not None:
                    self.bcd_uid += 1
                elif reemit_frame and self.last_p_frame is not None:
                    p_frame = self.last_p_frame

                if p_frame is not None:
                    # Frame is changed or reemit, construct new ds
                    self.last_p_frame = p_frame

                    bcd = BackendConnectionData(uid=self.bcd_uid)

                    bcd.assign_weak_heap(self.weak_heap)
                    bcd.set_is_frame_reemitted(reemit_frame)
                    bcd.set_frame_count(p_frame.frame_count)
                    bcd.set_frame_num(p_frame.frame_num)
                    bcd.set_frame_fps(p_frame.fps)
                    bcd.set_frame_timestamp(p_frame.timestamp)
                    bcd.set_frame_image_name(p_frame.name)

                    image = ImageProcessor(p_frame.image).to_uint8().get_image('HWC')
                    bcd.set_image(p_frame.name, image)

                    self.stop_profile_timing()
                    self.pending_bcd = bcd

        if self.pending_bcd is not None:
            if self.bc_out.is_full_read(1):
                self.bc_out.write(self.pending_bcd)
                self.pending_bcd = None

        time.sleep(0.001)

    def on_stop(self):
        self.set_fp(None)

class FPState(BackendWorkerState):
    target_width : int = None
    fps : float = None
    is_realtime : bool = None
    is_autorewind : bool = None

class WorkerState(BackendWorkerState):
    input_type : InputType = None
    input_path : Path = None
    fp_state : FPState = None


class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.input_type = lib_csw.DynamicSingleSwitch.Client()
            self.input_paths = lib_csw.Paths.Client()
            self.error = lib_csw.Error.Client()

            self.target_width = lib_csw.Number.Client()
            self.fps = lib_csw.Number.Client()

            self.is_realtime = lib_csw.Flag.Client()
            self.is_autorewind = lib_csw.Flag.Client()

            self.frame_index = lib_csw.Number.Client()
            self.frame_count = lib_csw.Number.Client()

            self.play = lib_csw.Signal.Client()
            self.pause = lib_csw.Signal.Client()
            self.seek_backward = lib_csw.Signal.Client()
            self.seek_forward = lib_csw.Signal.Client()
            self.seek_begin = lib_csw.Signal.Client()
            self.seek_end = lib_csw.Signal.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.input_type = lib_csw.DynamicSingleSwitch.Host()
            self.input_paths = lib_csw.Paths.Host()
            self.error = lib_csw.Error.Host()

            self.target_width = lib_csw.Number.Host()
            self.fps = lib_csw.Number.Host()
            self.is_realtime = lib_csw.Flag.Host()
            self.is_autorewind = lib_csw.Flag.Host()

            self.frame_index = lib_csw.Number.Host()
            self.frame_count = lib_csw.Number.Host()

            self.play = lib_csw.Signal.Host()
            self.pause = lib_csw.Signal.Host()
            self.seek_backward = lib_csw.Signal.Host()
            self.seek_forward = lib_csw.Signal.Host()
            self.seek_begin = lib_csw.Signal.Host()
            self.seek_end = lib_csw.Signal.Host()

