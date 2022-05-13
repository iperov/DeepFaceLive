import numpy as np
from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx

from ..backend import FaceDetector
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber


class QFaceDetector(QBackendPanel):
    def __init__(self, backend : FaceDetector):
        if not isinstance(backend, FaceDetector):
            raise ValueError('backend must be an instance of FaceDetector')

        self._backend = backend
        self._bc_out = backend.get_bc_out()
        self._weak_heap = backend.get_weak_heap()
        self._bcd_id = None
        self._timer = qtx.QXTimer(interval=10, timeout=self._on_timer_10ms, start=True)

        face_coords_label = self._q_face_coords_label = qtx.QXLabel(font=QXFontDB.get_fixedwidth_font(size=7), word_wrap=False)
        q_detected_faces  = self._q_detected_faces    = qtx.QXCollapsibleSection(title=L('@QFaceDetector.detected_faces'),
                                                                                 content_layout=qtx.QXVBoxLayout([face_coords_label]), is_opened=True)

        cs = backend.get_control_sheet()

        q_detector_type_label = QLabelPopupInfo(label=L('@QFaceDetector.detector_type'), popup_info_text=L('@QFaceDetector.help.detector_type') )
        q_detector_type       = QComboBoxCSWDynamicSingleSwitch(cs.detector_type, reflect_state_widgets=[q_detector_type_label])

        q_device_label        = QLabelPopupInfo(label=L('@common.device'), popup_info_text=L('@common.help.device') )
        q_device              = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_device_label])

        q_fixed_window_size_label = QLabelPopupInfo(label=L('@QFaceDetector.window_size'), popup_info_text=L('@QFaceDetector.help.window_size') )
        q_fixed_window_size   = QSpinBoxCSWNumber(cs.fixed_window_size, reflect_state_widgets=[q_fixed_window_size_label, q_detected_faces])

        q_threshold_label    = QLabelPopupInfo(label=L('@QFaceDetector.threshold'), popup_info_text=L('@QFaceDetector.help.threshold') )
        q_threshold          = QSpinBoxCSWNumber(cs.threshold, reflect_state_widgets=[q_threshold_label])

        q_max_faces_label    = QLabelPopupInfo(label=L('@QFaceDetector.max_faces'), popup_info_text=L('@QFaceDetector.help.max_faces') )
        q_max_faces          = QSpinBoxCSWNumber(cs.max_faces, reflect_state_widgets=[q_max_faces_label])

        q_sort_by_label    = QLabelPopupInfo(label=L('@QFaceDetector.sort_by'), popup_info_text=L('@QFaceDetector.help.sort_by') )
        q_sort_by            = QComboBoxCSWDynamicSingleSwitch(cs.sort_by, reflect_state_widgets=[q_sort_by_label])

        q_temporal_smoothing_label = QLabelPopupInfo(label=L('@QFaceDetector.temporal_smoothing'), popup_info_text=L('@QFaceDetector.help.temporal_smoothing') )
        q_temporal_smoothing = QSpinBoxCSWNumber(cs.temporal_smoothing, reflect_state_widgets=[q_temporal_smoothing_label])

        grid_l = qtx.QXGridLayout(vertical_spacing=5, horizontal_spacing=5)
        row = 0
        grid_l.addWidget(q_detector_type_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_detector_type, row, 1, 1, 3)
        row += 1
        grid_l.addWidget(q_device_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_device, row, 1, 1, 3)
        row += 1
        grid_l.addWidget(q_fixed_window_size_label, row, 0, 1, 2, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_fixed_window_size, row, 2, 1, 2, alignment=qtx.AlignLeft)
        row += 1
        grid_l.addWidget(q_threshold_label, row, 0, 1, 2, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_threshold, row, 2, 1, 2, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addLayout( qtx.QXHBoxLayout([q_max_faces_label, 5, q_max_faces]), row, 0, 1, 2, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addLayout( qtx.QXHBoxLayout([q_sort_by_label, 5,q_sort_by]), row, 2, 1,2, alignment=qtx.AlignLeft | qtx.AlignVCenter)
        row += 1
        grid_l.addLayout( qtx.QXHBoxLayout([q_temporal_smoothing_label, 5, q_temporal_smoothing]), row, 0, 1, 4, alignment=qtx.AlignCenter)
        row += 1
        grid_l.addWidget(q_detected_faces, row, 0, 1, 4)
        row += 1
        super().__init__(backend, L('@QFaceDetector.module_title'), layout=qtx.QXVBoxLayout([grid_l]))

    def _on_backend_state_change(self, backend, started, starting, stopping, stopped, busy):
        super()._on_backend_state_change (backend, started, starting, stopping, stopped, busy)

        if stopped:
            self._q_face_coords_label.clear()

    def _on_timer_10ms(self):

        if self._q_detected_faces.is_opened() and not self.get_top_QXWindow().is_minimized():
            bcd_id = self._bc_out.get_write_id()
            if self._bcd_id != bcd_id:
                # Has new bcd version
                bcd, self._bcd_id = self._bc_out.get_by_id(bcd_id), bcd_id

                if bcd is not None:
                    bcd.assign_weak_heap(self._weak_heap)

                    frame_image = bcd.get_image(bcd.get_frame_image_name())
                    frame_image_w_h = None
                    if frame_image is not None:
                        h,w = frame_image.shape[0:2]
                        frame_image_w_h = (w,h)

                    info = []
                    for face_id, fsi in enumerate(bcd.get_face_swap_info_list()):
                        info_str = f'{face_id}: '

                        if fsi.face_urect is not None:
                            l,t,r,b = fsi.face_urect.as_ltrb_bbox(frame_image_w_h).astype(np.int)
                            info_str += f'[{l},{t},{r},{b}]'

                        info.append(info_str)

                    info = '\n'.join(info)
                    self._q_face_coords_label.setText(info)
