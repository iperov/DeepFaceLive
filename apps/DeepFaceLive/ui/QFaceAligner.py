from localization import L
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as lib_qt

from ..backend import FaceAligner
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber


class QFaceAligner(QBackendPanel):
    def __init__(self, backend : FaceAligner):
        cs = backend.get_control_sheet()

        q_face_coverage_label = QLabelPopupInfo(label=L('@QFaceAligner.face_coverage'), popup_info_text=L('@QFaceAligner.help.face_coverage') )
        q_face_coverage       = QSpinBoxCSWNumber(cs.face_coverage, reflect_state_widgets=[q_face_coverage_label])

        q_resolution_label = QLabelPopupInfo(label=L('@QFaceAligner.resolution'), popup_info_text=L('@QFaceAligner.help.resolution') )
        q_resolution       = QSpinBoxCSWNumber(cs.resolution, reflect_state_widgets=[q_resolution_label])

        q_exclude_moving_parts_label = QLabelPopupInfo(label=L('@QFaceAligner.exclude_moving_parts'), popup_info_text=L('@QFaceAligner.help.exclude_moving_parts') )
        q_exclude_moving_parts = QCheckBoxCSWFlag(cs.exclude_moving_parts, reflect_state_widgets=[q_exclude_moving_parts_label])

        q_head_mode_label = QLabelPopupInfo(label=L('@QFaceAligner.head_mode'), popup_info_text=L('@QFaceAligner.help.head_mode') )
        q_head_mode = QCheckBoxCSWFlag(cs.head_mode, reflect_state_widgets=[q_head_mode_label])

        q_x_offset_label = QLabelPopupInfo(label=L('@QFaceAligner.x_offset'))
        q_x_offset       = QSpinBoxCSWNumber(cs.x_offset, reflect_state_widgets=[q_x_offset_label])

        q_y_offset_label = QLabelPopupInfo(label=L('@QFaceAligner.y_offset'))
        q_y_offset       = QSpinBoxCSWNumber(cs.y_offset, reflect_state_widgets=[q_y_offset_label])

        grid_l = lib_qt.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_face_coverage_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_face_coverage, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_resolution_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_resolution, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_exclude_moving_parts_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_exclude_moving_parts, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_head_mode_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_head_mode, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addLayout( lib_qt.QXVBoxLayout([q_x_offset_label, q_y_offset_label]), row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addLayout( lib_qt.QXHBoxLayout([q_x_offset, q_y_offset]), row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1

        super().__init__(backend, L('@QFaceAligner.module_title'),
                         layout=lib_qt.QXVBoxLayout([grid_l]))

