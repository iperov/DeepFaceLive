from localization import L
from xlib import qt as qtx

from ..backend import FaceAligner
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QComboBoxCSWDynamicSingleSwitch import QComboBoxCSWDynamicSingleSwitch

class QFaceAligner(QBackendPanel):
    def __init__(self, backend : FaceAligner):
        cs = backend.get_control_sheet()

        q_align_mode_label = QLabelPopupInfo(label=L('@QFaceAligner.align_mode'), popup_info_text=L('@QFaceAligner.help.align_mode'))
        q_align_mode = QComboBoxCSWDynamicSingleSwitch(cs.align_mode, reflect_state_widgets=[q_align_mode_label])

        q_face_coverage_label = QLabelPopupInfo(label=L('@QFaceAligner.face_coverage'), popup_info_text=L('@QFaceAligner.help.face_coverage') )
        q_face_coverage       = QSpinBoxCSWNumber(cs.face_coverage, reflect_state_widgets=[q_face_coverage_label])

        q_resolution_label = QLabelPopupInfo(label=L('@QFaceAligner.resolution'), popup_info_text=L('@QFaceAligner.help.resolution') )
        q_resolution       = QSpinBoxCSWNumber(cs.resolution, reflect_state_widgets=[q_resolution_label])

        q_exclude_moving_parts_label = QLabelPopupInfo(label=L('@QFaceAligner.exclude_moving_parts'), popup_info_text=L('@QFaceAligner.help.exclude_moving_parts') )
        q_exclude_moving_parts = QCheckBoxCSWFlag(cs.exclude_moving_parts, reflect_state_widgets=[q_exclude_moving_parts_label])

        q_head_mode_label = QLabelPopupInfo(label=L('@QFaceAligner.head_mode'), popup_info_text=L('@QFaceAligner.help.head_mode') )
        q_head_mode = QCheckBoxCSWFlag(cs.head_mode, reflect_state_widgets=[q_head_mode_label])

        q_freeze_z_rotation_label = QLabelPopupInfo(label=L('@QFaceAligner.freeze_z_rotation') )
        q_freeze_z_rotation = QCheckBoxCSWFlag(cs.freeze_z_rotation, reflect_state_widgets=[q_freeze_z_rotation_label])

        q_x_offset_label = QLabelPopupInfo(label=L('@QFaceAligner.x_offset'))
        q_x_offset       = QSpinBoxCSWNumber(cs.x_offset, reflect_state_widgets=[q_x_offset_label])

        q_y_offset_label = QLabelPopupInfo(label=L('@QFaceAligner.y_offset'))
        q_y_offset       = QSpinBoxCSWNumber(cs.y_offset, reflect_state_widgets=[q_y_offset_label])

        grid_l = qtx.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_align_mode_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_align_mode, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_face_coverage_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_face_coverage, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_resolution_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_resolution, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_exclude_moving_parts_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_exclude_moving_parts, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_head_mode_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_head_mode, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_freeze_z_rotation_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_freeze_z_rotation, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addLayout( qtx.QXVBoxLayout([q_x_offset_label, q_y_offset_label]), row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addLayout( qtx.QXHBoxLayout([q_x_offset, q_y_offset]), row, 1, alignment=qtx.AlignLeft )
        row += 1

        super().__init__(backend, L('@QFaceAligner.module_title'),
                         layout=qtx.QXVBoxLayout([grid_l]))

