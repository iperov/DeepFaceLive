from pathlib import Path
from typing import List

from localization import L, Localization
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import os as lib_os
from xlib import qt as lib_qt
from xlib.qt.widgets.QXLabel import QXLabel

from . import backend
from .ui.QCameraSource import QCameraSource
from .ui.QFaceAligner import QFaceAligner
from .ui.QFaceDetector import QFaceDetector
from .ui.QFaceMarker import QFaceMarker
from .ui.QFaceMerger import QFaceMerger
from .ui.QFaceSwapper import QFaceSwapper
from .ui.QFileSource import QFileSource
from .ui.QFrameAdjuster import QFrameAdjuster
from .ui.QStreamOutput import QStreamOutput
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer


class QLiveSwap(lib_qt.QXWidget):
    def __init__(self, userdata_path : Path,
                       settings_dirpath : Path):
        super().__init__()

        dfm_models_path = userdata_path / 'dfm_models'
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / 'output_sequence'
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Construct backend config

        backend_db          = self.backend_db          = backend.BackendDB( settings_dirpath / 'states.dat' )
        backed_weak_heap    = self.backed_weak_heap    = backend.BackendWeakHeap(size_mb=1024)
        reemit_frame_signal = self.reemit_frame_signal = backend.BackendSignal()

        multi_sources_bc_out  = backend.BackendConnection(multi_producer=True)
        face_detector_bc_out  = backend.BackendConnection()
        face_marker_bc_out    = backend.BackendConnection()
        face_aligner_bc_out   = backend.BackendConnection()
        face_swapper_bc_out   = backend.BackendConnection()
        frame_adjuster_bc_out = backend.BackendConnection()
        face_merger_bc_out    = backend.BackendConnection()

        file_source    = self.file_source    = backend.FileSource   (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_out=multi_sources_bc_out, backend_db=backend_db)
        camera_source  = self.camera_source  = backend.CameraSource (weak_heap=backed_weak_heap, bc_out=multi_sources_bc_out, backend_db=backend_db)
        face_detector  = self.face_detector  = backend.FaceDetector (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=multi_sources_bc_out, bc_out=face_detector_bc_out, backend_db=backend_db )
        face_marker    = self.face_marker    = backend.FaceMarker   (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_detector_bc_out, bc_out=face_marker_bc_out, backend_db=backend_db)
        face_aligner   = self.face_aligner   = backend.FaceAligner  (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_marker_bc_out, bc_out=face_aligner_bc_out, backend_db=backend_db )
        face_swapper   = self.face_swapper   = backend.FaceSwapper  (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_swapper_bc_out, dfm_models_path=dfm_models_path, backend_db=backend_db )
        frame_adjuster = self.frame_adjuster = backend.FrameAdjuster(weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_swapper_bc_out, bc_out=frame_adjuster_bc_out, backend_db=backend_db )
        face_merger    = self.face_merger    = backend.FaceMerger   (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=frame_adjuster_bc_out, bc_out=face_merger_bc_out, backend_db=backend_db )
        stream_output  = self.stream_output  = backend.StreamOutput (weak_heap=backed_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_merger_bc_out, save_default_path=userdata_path, backend_db=backend_db)

        self.all_backends : List[backend.BackendHost] = [file_source, camera_source, face_detector, face_marker, face_aligner, face_swapper, frame_adjuster, face_merger, stream_output]

        self.q_file_source    = QFileSource(self.file_source)
        self.q_camera_source  = QCameraSource(self.camera_source)
        self.q_face_detector  = QFaceDetector(self.face_detector)
        self.q_face_marker    = QFaceMarker(self.face_marker)
        self.q_face_aligner   = QFaceAligner(self.face_aligner)
        self.q_face_swapper   = QFaceSwapper(self.face_swapper, dfm_models_path=dfm_models_path)
        self.q_frame_adjuster = QFrameAdjuster(self.frame_adjuster)
        self.q_face_merger    = QFaceMerger(self.face_merger)
        self.q_stream_output  = QStreamOutput(self.stream_output)

        self.q_ds_frame_viewer = QBCFrameViewer(backed_weak_heap, multi_sources_bc_out)
        self.q_ds_fa_viewer    = QBCFaceAlignViewer(backed_weak_heap, face_aligner_bc_out, preview_width=256)
        self.q_ds_fc_viewer    = QBCFaceSwapViewer(backed_weak_heap, face_swapper_bc_out, preview_width=256)
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(backed_weak_heap, face_merger_bc_out)

        q_nodes = lib_qt.QXWidget(size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
                     layout=lib_qt.QXHBoxLayout([
                        lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_file_source, self.q_camera_source], spacing=5),  fixed_width=256 ),
                        lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_face_detector,  self.q_face_aligner,], spacing=5),  fixed_width=256),
                        lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_face_marker, self.q_face_swapper], spacing=5),  fixed_width=256),
                        lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_frame_adjuster, self.q_face_merger, self.q_stream_output, ], spacing=5),  fixed_width=256),
                        ], spacing=5))

        q_view_nodes = lib_qt.QXWidget(size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
                          layout=lib_qt.QXHBoxLayout([
                            (lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_ds_frame_viewer]), fixed_width=256 ), Qt.AlignmentFlag.AlignTop),
                            (lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_ds_fa_viewer]), fixed_width=256 ), Qt.AlignmentFlag.AlignTop),
                            (lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_ds_fc_viewer]), fixed_width=256 ), Qt.AlignmentFlag.AlignTop),
                            (lib_qt.QXWidget(layout=lib_qt.QXVBoxLayout([self.q_ds_merged_frame_viewer]), fixed_width=256 ), Qt.AlignmentFlag.AlignTop),
                            ], spacing=5))

        self.setLayout(lib_qt.QXVBoxLayout(
                       [  (lib_qt.QXWidget( layout=lib_qt.QXVBoxLayout([
                                            (q_nodes, Qt.AlignmentFlag.AlignTop),
                                            (q_view_nodes, Qt.AlignmentFlag.AlignHCenter),
                                            ], spacing=5)),
                           Qt.AlignmentFlag.AlignCenter),
                       ]))

        self._timer = lib_qt.QXTimer(interval=5, timeout=self._on_timer_5ms, start=True)


    def _process_messages(self):
        self.backend_db.process_messages()
        for backend in self.all_backends:
            backend.process_messages()

    def _on_timer_5ms(self):
        self._process_messages()

    def clear_backend_db(self):
        self.backend_db.clear()

    def initialize(self):
        for backend in self.all_backends:
            backend.restore_on_off_state()

    def finalize(self):
        # Gracefully stop the backend
        for backend in self.all_backends:
            while backend.is_starting() or backend.is_stopping():
                self._process_messages()

            backend.save_on_off_state()
            backend.stop()

        while not all( x.is_stopped() for x in self.all_backends ):
            self._process_messages()

        self.backend_db.finish_pending_jobs()

        self.q_ds_frame_viewer.clear()
        self.q_ds_fa_viewer.clear()

class QDFLAppWindow(lib_qt.QXWindow):

    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True, size_policy=(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum) )

        self._userdata_path = userdata_path
        self._settings_dirpath = settings_dirpath

        menu_bar = lib_qt.QXMenuBar( font=QXFontDB.get_default_font(size=10), size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding) )
        menu_file = menu_bar.addMenu( L('@QDFLAppWindow.file') )
        menu_language = menu_bar.addMenu( L('@QDFLAppWindow.language') )

        menu_file_action_reinitialize = menu_file.addAction( L('@QDFLAppWindow.reinitialize') )
        menu_file_action_reinitialize.triggered.connect(lambda: lib_qt.QXMainApplication.get_singleton().reinitialize() )

        menu_file_action_reset_settings = menu_file.addAction( L('@QDFLAppWindow.reset_modules_settings') )
        menu_file_action_reset_settings.triggered.connect(self._on_reset_modules_settings)

        menu_file_action_quit = menu_file.addAction( L('@QDFLAppWindow.quit') )
        menu_file_action_quit.triggered.connect(lambda: lib_qt.QXMainApplication.quit() )

        menu_language_action_english = menu_language.addAction('English' )
        menu_language_action_english.triggered.connect(lambda: (lib_qt.QXMainApplication.get_singleton().set_language('en-US'), lib_qt.QXMainApplication.get_singleton().reinitialize()) )

        menu_language_action_russian = menu_language.addAction('Русский')
        menu_language_action_russian.triggered.connect(lambda: (lib_qt.QXMainApplication.get_singleton().set_language('ru-RU'), lib_qt.QXMainApplication.get_singleton().reinitialize()) )

        menu_language_action_chinesse = menu_language.addAction('汉语')
        menu_language_action_chinesse.triggered.connect(lambda: (lib_qt.QXMainApplication.get_singleton().set_language('zh-CN'), lib_qt.QXMainApplication.get_singleton().reinitialize()) )

        menu_help = menu_bar.addMenu( L('@QDFLAppWindow.help') )
        menu_help_action_github = menu_help.addAction( L('@QDFLAppWindow.visit_github_page') )
        menu_help_action_github.triggered.connect(lambda: QDesktopServices.openUrl(QUrl('https://github.com/iperov/DeepFaceLive' )))

        self.q_live_swap = None
        self.q_live_swap_container = lib_qt.QXWidget()

        self.content_l = lib_qt.QXVBoxLayout()

        cb_process_priority = self._cb_process_priority = lib_qt.QXSaveableComboBox(
                                                db_key = '_QDFLAppWindow_process_priority',
                                                choices=[lib_os.ProcessPriority.NORMAL, lib_os.ProcessPriority.IDLE],
                                                default_choice=lib_os.ProcessPriority.NORMAL,
                                                choices_names=[ L('@QDFLAppWindow.process_priority.normal'), L('@QDFLAppWindow.process_priority.lowest') ],
                                                on_choice_selected=self._on_cb_process_priority_choice)

        menu_bar_tail = lib_qt.QXFrame(layout=lib_qt.QXHBoxLayout([
                                       10,
                                       QXLabel(text=L('@QDFLAppWindow.process_priority')),
                                       4,
                                       cb_process_priority,
                                       ]),
                                       size_policy=(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))

        self.setLayout( lib_qt.QXVBoxLayout([ lib_qt.QXWidget(layout=lib_qt.QXHBoxLayout([menu_bar, menu_bar_tail, lib_qt.QXFrame() ]), size_policy=(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)),
                                                5,
                                                lib_qt.QXWidget(layout=self.content_l)
                                            ] ))

        self.call_on_closeEvent(self._on_closeEvent)

        q_live_swap = self.q_live_swap = QLiveSwap(userdata_path=self._userdata_path, settings_dirpath=self._settings_dirpath)
        q_live_swap.initialize()
        self.content_l.addWidget(q_live_swap)

    def _on_reset_modules_settings(self):
        if self.q_live_swap is not None:
            self.q_live_swap.clear_backend_db()
            lib_qt.QXMainApplication.get_singleton().reinitialize()

    def _on_cb_process_priority_choice(self, prio : lib_os.ProcessPriority, _):
        lib_os.set_process_priority(prio)

        if self.q_live_swap is not None:
            lib_qt.QXMainApplication.get_singleton().reinitialize()

    def finalize(self):
        self.q_live_swap.finalize()

    def _on_closeEvent(self):
        self.finalize()

class QSplashWindow(lib_qt.QXWindow):
    def __init__(self, next_window=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen)

        logo_deepfacelive = lib_qt.QXLabel(image=QXImageDB.splash_deepfacelive())
        self.setLayout( lib_qt.QXVBoxLayout([
                          ( lib_qt.QXHBoxLayout([logo_deepfacelive]), Qt.AlignmentFlag.AlignCenter),
                        ], spacing=0, contents_margins=20))

class DeepFaceLiveApp(lib_qt.QXMainApplication):
    def __init__(self, userdata_path):
        self.userdata_path = userdata_path
        settings_dirpath = self.settings_dirpath =  userdata_path / 'settings'
        if not settings_dirpath.exists():
            settings_dirpath.mkdir(parents=True)
        super().__init__(app_name='DeepFaceLive', settings_dirpath=settings_dirpath)

        self.setFont( QXFontDB.get_default_font() )
        self.setWindowIcon( QXImageDB.app_icon().as_QIcon() )

        splash_wnd = self.splash_wnd = QSplashWindow()
        splash_wnd.show()
        splash_wnd.center_on_screen()

        self._dfl_wnd = None
        self.initialize()
        self._t = lib_qt.QXTimer(interval=1666, timeout=self._on_splash_wnd_expired, single_shot=True, start=True)

    def on_reinitialize(self):
        self.finalize()

        import gc
        gc.collect()
        gc.collect()

        self.initialize()
        self._dfl_wnd.show()

    def initialize(self):
        Localization.set_language( self.get_language() )

        if self._dfl_wnd is None:
            self._dfl_wnd = QDFLAppWindow(userdata_path=self.userdata_path, settings_dirpath=self.settings_dirpath)

    def finalize(self):
        if self._dfl_wnd is not None:
            self._dfl_wnd.close()
            self._dfl_wnd.deleteLater()
            self._dfl_wnd = None

    def _on_splash_wnd_expired(self):
        self._dfl_wnd.show()

        if self.splash_wnd is not None:
            self.splash_wnd.hide()
            self.splash_wnd.deleteLater()
            self.splash_wnd = None






#import gc
#gc.collect()
#gc.collect()

# def _reinitialize(self, init_new=True):
#     if self.q_live_swap is not None:
#         self.content_l.removeWidget(self.q_live_swap)
#         self.q_live_swap.finalize()

#         self.q_live_swap.deleteLater()
#         self.q_live_swap = None

#         import gc
#         gc.collect()
#         gc.collect()

#     LStrings.initialize()

#     if init_new:
#         self.q_live_swap = QLiveSwap(userdata_path=self._userdata_path, settings_dirpath=self._settings_dirpath)
#         self.q_live_swap.initialize()
#         self.content_l.addWidget(self.q_live_swap)
#self._reinitialize(init_new=False)
