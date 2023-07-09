from pathlib import Path

from localization import L
from resources.gfx import QXImageDB
from xlib import qt as qtx

from ..backend import FaceSwapInsight
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSliderCSWNumber import QSliderCSWNumber
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal


class QFaceSwapInsight(QBackendPanel):
    def __init__(self, backend : FaceSwapInsight, faces_path : Path):
        self._faces_path = faces_path

        cs = backend.get_control_sheet()

        btn_open_folder = self.btn_open_folder = qtx.QXPushButton(image = QXImageDB.eye_outline('light gray'), tooltip_text='Reveal in Explorer', released=self._btn_open_folder_released, fixed_size=(24,22) )

        q_device_label  = QLabelPopupInfo(label=L('@common.device'), popup_info_text=L('@common.help.device') )
        q_device        = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_device_label])

        q_face_label = QLabelPopupInfo(label=L('@QFaceSwapInsight.face') )
        q_face       = QComboBoxCSWDynamicSingleSwitch(cs.face, reflect_state_widgets=[q_face_label, btn_open_folder])

        q_adjust_c_label = QLabelPopupInfo(label='C')
        q_adjust_c       = QSliderCSWNumber(cs.adjust_c, reflect_state_widgets=[q_adjust_c_label])

        q_adjust_x_label = QLabelPopupInfo(label='X')
        q_adjust_x       = QSliderCSWNumber(cs.adjust_x, reflect_state_widgets=[q_adjust_x_label])

        q_adjust_y_label = QLabelPopupInfo(label='Y')
        q_adjust_y       = QSliderCSWNumber(cs.adjust_y, reflect_state_widgets=[q_adjust_y_label])

        q_animator_face_id_label = QLabelPopupInfo(label=L('@common.face_id') )
        q_animator_face_id       = QSpinBoxCSWNumber(cs.animator_face_id, reflect_state_widgets=[q_animator_face_id_label])

        q_update_faces = QXPushButtonCSWSignal(cs.update_faces, image=QXImageDB.reload_outline('light gray'), button_size=(24,22) )

        grid_l = qtx.QXGridLayout( spacing=5)
        row = 0
        grid_l.addWidget(q_device_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_device, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_face_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addLayout(qtx.QXHBoxLayout([q_face, 2, btn_open_folder, 2, q_update_faces]), row, 1 )
        row += 1
        grid_l.addWidget(q_adjust_c_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_adjust_c, row, 1 )
        row += 1
        grid_l.addWidget(q_adjust_x_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_adjust_x, row, 1 )
        row += 1
        grid_l.addWidget(q_adjust_y_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_adjust_y, row, 1 )
        row += 1
        grid_l.addWidget(q_animator_face_id_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_animator_face_id, row, 1, alignment=qtx.AlignLeft )

        row += 1

        super().__init__(backend, L('@QFaceSwapInsight.module_title'),
                         layout=qtx.QXVBoxLayout([grid_l]) )

    def _btn_open_folder_released(self):
        qtx.QDesktopServices.openUrl(qtx.QUrl.fromLocalFile( str(self._faces_path) ))
