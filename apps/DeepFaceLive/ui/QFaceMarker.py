from localization import L
from xlib import qt as qtx

from .widgets.QBackendPanel import QBackendPanel
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber


class QFaceMarker(QBackendPanel):
    def __init__(self, backend):
        cs = backend.get_control_sheet()

        q_marker_type_label  = QLabelPopupInfo(label=L('@QFaceMarker.marker_type'), popup_info_text=L('@QFaceMarker.help.marker_type') )
        q_marker_type        = QComboBoxCSWDynamicSingleSwitch(cs.marker_type, reflect_state_widgets=[q_marker_type_label])

        q_device_label       = QLabelPopupInfo(label=L('@common.device'), popup_info_text=L('@common.help.device') )
        q_device             = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_device_label])

        q_marker_coverage_label = QLabelPopupInfo(label=L('@QFaceMarker.marker_coverage'), popup_info_text=L('@QFaceMarker.help.marker_coverage') )
        q_marker_coverage       = QSpinBoxCSWNumber(cs.marker_coverage, reflect_state_widgets=[q_marker_coverage_label])

        q_temporal_smoothing_label = QLabelPopupInfo(label=L('@QFaceMarker.temporal_smoothing'), popup_info_text=L('@QFaceMarker.help.temporal_smoothing') )
        q_temporal_smoothing = QSpinBoxCSWNumber(cs.temporal_smoothing, reflect_state_widgets=[q_temporal_smoothing_label])

        grid_l = qtx.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_marker_type_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_marker_type, row, 1, 1, 3 )
        row += 1
        grid_l.addWidget(q_device_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_device, row, 1, 1, 3 )
        row += 1

        sub_row = 0
        sub_grid_l = qtx.QXGridLayout(spacing=5)
        sub_grid_l.addWidget(q_marker_coverage_label, sub_row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        sub_grid_l.addWidget(q_marker_coverage, sub_row, 1, 1, 1, alignment=qtx.AlignLeft )
        sub_row += 1
        sub_grid_l.addWidget(q_temporal_smoothing_label, sub_row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        sub_grid_l.addWidget(q_temporal_smoothing, sub_row, 1, 1, 1, alignment=qtx.AlignLeft )
        sub_row += 1

        grid_l.addLayout(sub_grid_l, row, 0, 1, 4, alignment=qtx.AlignCenter )
        row += 1

        super().__init__(backend, L('@QFaceMarker.module_title'),
                         layout=qtx.QXVBoxLayout([grid_l]) )








