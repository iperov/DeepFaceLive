from localization import L
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xlib import qt as lib_qt

from .widgets.QBackendPanel import QBackendPanel
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSliderCSWNumber import QSliderCSWNumber
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber


class QFaceMerger(QBackendPanel):
    def __init__(self, backend):
        cs = backend.get_control_sheet()

        q_device_label = QLabelPopupInfo(label=L('@QFaceMerger.device'), popup_info_text=L('@QFaceMerger.help.device'))
        q_device       = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_device_label])

        q_face_x_offset_label = QLabelPopupInfo(label=L('@QFaceMerger.face_x_offset'))
        q_face_x_offset       = QSpinBoxCSWNumber(cs.face_x_offset, reflect_state_widgets=[q_face_x_offset_label])

        q_face_y_offset_label = QLabelPopupInfo(label=L('@QFaceMerger.face_y_offset'))
        q_face_y_offset       = QSpinBoxCSWNumber(cs.face_y_offset, reflect_state_widgets=[q_face_y_offset_label])

        q_face_scale_label = QLabelPopupInfo(label=L('@QFaceMerger.face_scale') )
        q_face_scale       = QSpinBoxCSWNumber(cs.face_scale, reflect_state_widgets=[q_face_scale_label])

        q_face_mask_type_label = QLabelPopupInfo(label=L('@QFaceMerger.face_mask_type') )
        q_face_mask_type       = QComboBoxCSWDynamicSingleSwitch(cs.face_mask_type, reflect_state_widgets=[q_face_mask_type_label])

        q_face_mask_erode_label = QLabelPopupInfo(label=L('@QFaceMerger.face_mask_erode') )
        q_face_mask_erode       = QSpinBoxCSWNumber(cs.face_mask_erode, reflect_state_widgets=[q_face_mask_erode_label])

        q_face_mask_blur_label = QLabelPopupInfo(label=L('@QFaceMerger.face_mask_blur') )
        q_face_mask_blur       = QSpinBoxCSWNumber(cs.face_mask_blur, reflect_state_widgets=[q_face_mask_blur_label])
        
        q_interpolation_label = QLabelPopupInfo(label=L('@QFaceMerger.interpolation') )
        q_interpolation       = QComboBoxCSWDynamicSingleSwitch(cs.interpolation, reflect_state_widgets=[q_interpolation_label])

        q_face_opacity_label = QLabelPopupInfo(label=L('@QFaceMerger.face_opacity') )
        q_face_opacity       = QSliderCSWNumber(cs.face_opacity, reflect_state_widgets=[q_face_opacity_label])

        grid_l = lib_qt.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_device_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_device, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addLayout( lib_qt.QXVBoxLayout([q_face_x_offset_label, q_face_y_offset_label]), row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addLayout( lib_qt.QXHBoxLayout([q_face_x_offset, q_face_y_offset]), row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_face_scale_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_face_scale, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_face_mask_type_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_face_mask_type, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addLayout(lib_qt.QXVBoxLayout([q_face_mask_erode_label,q_face_mask_blur_label]), row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addLayout(lib_qt.QXHBoxLayout([q_face_mask_erode,q_face_mask_blur], spacing=3), row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_interpolation_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_interpolation, row, 1, alignment=Qt.AlignmentFlag.AlignLeft )
        row += 1
        grid_l.addWidget(q_face_opacity_label, row, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter  )
        grid_l.addWidget(q_face_opacity, row, 1)
        row += 1

        super().__init__(backend, L('@QFaceMerger.module_title'),
                         layout=lib_qt.QXVBoxLayout([grid_l]) )

