from pathlib import Path

from localization import L
from resources.gfx import QXImageDB
from xlib import qt as qtx

from ..backend import FaceAnimator
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber

from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal
from .widgets.QSliderCSWNumber import QSliderCSWNumber

class QFaceAnimator(QBackendPanel):
    def __init__(self, backend : FaceAnimator, animatables_path : Path):
        self._animatables_path = animatables_path

        cs = backend.get_control_sheet()

        btn_open_folder = self.btn_open_folder = qtx.QXPushButton(image = QXImageDB.eye_outline('light gray'), tooltip_text='Reveal in Explorer', released=self._btn_open_folder_released, fixed_size=(24,22) )

        q_device_label  = QLabelPopupInfo(label=L('@common.device'), popup_info_text=L('@common.help.device') )
        q_device        = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_device_label])

        q_animatable_label = QLabelPopupInfo(label=L('@QFaceAnimator.animatable') )
        q_animatable       = QComboBoxCSWDynamicSingleSwitch(cs.animatable, reflect_state_widgets=[q_animatable_label, btn_open_folder])

        q_animator_face_id_label = QLabelPopupInfo(label=L('@QFaceAnimator.animator_face_id') )
        q_animator_face_id       = QSpinBoxCSWNumber(cs.animator_face_id, reflect_state_widgets=[q_animator_face_id_label])
        
        q_relative_power_label = QLabelPopupInfo(label=L('@QFaceAnimator.relative_power') )
        q_relative_power = QSliderCSWNumber(cs.relative_power, reflect_state_widgets=[q_relative_power_label])

        q_update_animatables = QXPushButtonCSWSignal(cs.update_animatables, image=QXImageDB.reload_outline('light gray'), button_size=(24,22) )

        q_reset_reference_pose = QXPushButtonCSWSignal(cs.reset_reference_pose, text=L('@QFaceAnimator.reset_reference_pose') )

        grid_l = qtx.QXGridLayout( spacing=5)
        row = 0
        grid_l.addWidget(q_device_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_device, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_animatable_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addLayout(qtx.QXHBoxLayout([q_animatable, 2, btn_open_folder, 2, q_update_animatables]), row, 1 )
        row += 1
        grid_l.addWidget(q_animator_face_id_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_animator_face_id, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_relative_power_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_relative_power, row, 1 )

        row += 1
        grid_l.addWidget(q_reset_reference_pose, row, 0, 1, 2  )
        row += 1

        super().__init__(backend, L('@QFaceAnimator.module_title'),
                         layout=qtx.QXVBoxLayout([grid_l]) )

    def _btn_open_folder_released(self):
        qtx.QDesktopServices.openUrl(qtx.QUrl.fromLocalFile( str(self._animatables_path) ))
