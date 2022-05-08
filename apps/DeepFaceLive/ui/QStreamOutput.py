from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from ..backend import StreamOutput
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QLabelCSWNumber import QLabelCSWNumber
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QLineEditCSWText import QLineEditCSWText
from .widgets.QPathEditCSWPaths import QPathEditCSWPaths
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal


class QStreamOutput(QBackendPanel):
    def __init__(self, backend : StreamOutput):
        cs = backend.get_control_sheet()

        q_average_fps_label = QLabelPopupInfo(label=L('@QStreamOutput.avg_fps'), popup_info_text=L('@QStreamOutput.help.avg_fps'))
        q_average_fps       = QLabelCSWNumber(cs.avg_fps, reflect_state_widgets=[q_average_fps_label])

        q_source_type_label = QLabelPopupInfo(label=L('@QStreamOutput.source_type') )
        q_source_type       = QComboBoxCSWDynamicSingleSwitch(cs.source_type, reflect_state_widgets=[q_source_type_label])

        q_show_hide_window = QXPushButtonCSWSignal(cs.show_hide_window, text=L('@QStreamOutput.show_hide_window'), button_size=(None,22) )

        q_aligned_face_id_label = QLabelPopupInfo(label=L('@QStreamOutput.aligned_face_id'), popup_info_text=L('@QStreamOutput.help.aligned_face_id'))
        q_aligned_face_id       = QSpinBoxCSWNumber(cs.aligned_face_id, reflect_state_widgets=[q_aligned_face_id_label])

        q_target_delay_label = QLabelPopupInfo(label=L('@QStreamOutput.target_delay'), popup_info_text=L('@QStreamOutput.help.target_delay'))
        q_target_delay       = QSpinBoxCSWNumber(cs.target_delay, reflect_state_widgets=[q_target_delay_label])

        q_save_sequence_path_label = QLabelPopupInfo(label=L('@QStreamOutput.save_sequence_path'), popup_info_text=L('@QStreamOutput.help.save_sequence_path'))
        q_save_sequence_path       = QPathEditCSWPaths(cs.save_sequence_path, reflect_state_widgets=[q_target_delay_label, q_save_sequence_path_label])
        q_save_sequence_path_error = QErrorCSWError(cs.save_sequence_path_error)

        q_save_fill_frame_gap_label = QLabelPopupInfo(label=L('@QStreamOutput.save_fill_frame_gap'), popup_info_text=L('@QStreamOutput.help.save_fill_frame_gap'))
        q_save_fill_frame_gap       = QCheckBoxCSWFlag(cs.save_fill_frame_gap, reflect_state_widgets=[q_save_fill_frame_gap_label])

        q_is_streaming_label = QLabelPopupInfo(label='mpegts udp://')
        q_is_streaming       = QCheckBoxCSWFlag(cs.is_streaming, reflect_state_widgets=[q_is_streaming_label])

        q_stream_addr = QLineEditCSWText(cs.stream_addr, font=QXFontDB.get_fixedwidth_font())
        q_stream_port = QSpinBoxCSWNumber(cs.stream_port)

        grid_l = qtx.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_average_fps_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addWidget(q_average_fps, row, 1, 1, 2, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        row += 1
        grid_l.addWidget(q_source_type_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addWidget(q_source_type, row, 1, 1, 1, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        grid_l.addWidget(q_show_hide_window, row, 2, 1, 1)

        row += 1
        grid_l.addWidget(q_aligned_face_id_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addWidget(q_aligned_face_id, row, 1, 1, 2, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        row += 1
        grid_l.addWidget(q_target_delay_label, row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addWidget(q_target_delay, row, 1, 1, 2, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        row += 1

        grid_l.addWidget(q_save_sequence_path_label, row, 0,  1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addWidget(q_save_sequence_path, row, 1,  1, 2, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        row += 1
        grid_l.addLayout( qtx.QXHBoxLayout([q_save_fill_frame_gap, 4, q_save_fill_frame_gap_label]), row, 1, 1, 2, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        row += 1
        grid_l.addWidget(q_save_sequence_path_error, row, 0, 1, 3)
        row += 1
        grid_l.addLayout( qtx.QXHBoxLayout([q_is_streaming, 4, q_is_streaming_label]), row, 0, 1, 1, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addLayout( qtx.QXHBoxLayout([q_stream_addr, qtx.QXLabel(text=':'), q_stream_port]), row, 1, 1, 2, alignment=qtx.AlignLeft | qtx.AlignVCenter )
        row += 1

        super().__init__(backend, L('@QStreamOutput.module_title'),
                         layout=grid_l)
