from localization import L
from resources.gfx import QXImageDB
from xlib import qt as qtx

from ..backend import FileSource
from .widgets.QBackendPanel import QBackendPanel
from .widgets.QButtonCSWDynamicSingleSwitch import \
    QButtonCSWDynamicSingleSwitch
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QPathEditCSWPaths import QPathEditCSWPaths
from .widgets.QSliderCSWNumbers import QSliderCSWNumbers
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal


class QFileSource(QBackendPanel):
    def __init__(self, backend : FileSource):
        cs = backend.get_control_sheet()

        q_input_type  = QButtonCSWDynamicSingleSwitch(cs.input_type, horizontal=True, radio_buttons=True)
        q_input_paths = QPathEditCSWPaths(cs.input_paths)
        q_error       = QErrorCSWError(cs.error)

        q_target_width_label = QLabelPopupInfo(label=L('@QFileSource.target_width'), popup_info_text=L('@QFileSource.help.target_width') )
        q_target_width       = QSpinBoxCSWNumber(cs.target_width, reflect_state_widgets=[q_target_width_label])

        q_fps_label = QLabelPopupInfo(label=L('@QFileSource.fps'), popup_info_text=L('@QFileSource.help.fps') )
        q_fps       = QSpinBoxCSWNumber(cs.fps, reflect_state_widgets=[q_fps_label])

        q_is_realtime_label = QLabelPopupInfo(label=L('@QFileSource.is_realtime'), popup_info_text=L('@QFileSource.help.is_realtime') )
        q_is_realtime       = QCheckBoxCSWFlag(cs.is_realtime, reflect_state_widgets=[q_is_realtime_label])

        q_is_autorewind_label = QLabelPopupInfo(label=L('@QFileSource.is_autorewind'))
        q_is_autorewind       = QCheckBoxCSWFlag(cs.is_autorewind, reflect_state_widgets=[q_is_autorewind_label])

        btn_size = (32,32)
        btn_color = '#E01010'
        btn_seek_begin    = QXPushButtonCSWSignal(cs.seek_begin,    image=QXImageDB.play_skip_back_circle_outline(btn_color),    button_size=btn_size )
        btn_seek_backward = QXPushButtonCSWSignal(cs.seek_backward, image=QXImageDB.play_back_circle_outline(btn_color),         button_size=btn_size )
        btn_play          = QXPushButtonCSWSignal(cs.play,          image=QXImageDB.play_circle_outline(btn_color),              button_size=btn_size )
        btn_pause         = QXPushButtonCSWSignal(cs.pause,         image=QXImageDB.pause_circle_outline(btn_color),             button_size=btn_size )
        btn_seek_forward  = QXPushButtonCSWSignal(cs.seek_forward,  image=QXImageDB.play_forward_circle_outline(btn_color),      button_size=btn_size )
        btn_seek_end      = QXPushButtonCSWSignal(cs.seek_end,      image=QXImageDB.play_skip_forward_circle_outline(btn_color), button_size=btn_size )

        q_frame_slider = QSliderCSWNumbers(cs.frame_index, cs.frame_count)

        grid_l = qtx.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_target_width_label, row, 0, 1, 2, alignment=qtx.AlignRight | qtx.AlignVCenter )
        grid_l.addWidget(q_target_width, row, 2, 1, 2, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addLayout( qtx.QXHBoxLayout([q_is_realtime_label, 5, q_is_realtime, 5, q_fps_label]), row, 0, 1, 2, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget( q_fps, row, 2, 1, 2, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget( q_is_autorewind_label, row, 0, 1, 2, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget( q_is_autorewind, row, 2, 1, 2, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(qtx.QXFrameHBox([btn_seek_begin, btn_seek_backward, btn_play, btn_pause,btn_seek_forward, btn_seek_end], spacing=1),
                         row, 0, 1, 4, alignment=qtx.AlignCenter)
        row += 1
        grid_l.addWidget(q_frame_slider, row, 0, 1, 4)
        row += 1

        main_l = qtx.QXVBoxLayout([q_input_type,
                                   q_input_paths,
                                   q_error,
                                   grid_l], spacing=5)

        super().__init__(backend, L('@QFileSource.module_title'),
                         layout=main_l, content_align_top=True)

