from localization import L
from xlib import qt as qtx

from .widgets.QBackendPanel import QBackendPanel
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSliderCSWNumber import QSliderCSWNumber


class QFrameAdjuster(QBackendPanel):
    def __init__(self, backend):
        cs = backend.get_control_sheet()

        q_median_blur_label = QLabelPopupInfo(label=L('@QFrameAdjuster.median_blur_per'), popup_info_text=L('@QFrameAdjuster.help.median_blur_per') )
        q_median_blur       = QSliderCSWNumber(cs.median_blur_per, reflect_state_widgets=[q_median_blur_label])

        q_degrade_bicubic_label = QLabelPopupInfo(label=L('@QFrameAdjuster.degrade_bicubic_per'), popup_info_text=L('@QFrameAdjuster.help.degrade_bicubic_per') )
        q_degrade_bicubic       = QSliderCSWNumber(cs.degrade_bicubic_per, reflect_state_widgets=[q_degrade_bicubic_label])

        grid_l = qtx.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_median_blur_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_median_blur, row, 1)
        row += 1
        grid_l.addWidget(q_degrade_bicubic_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter  )
        grid_l.addWidget(q_degrade_bicubic, row, 1)
        row += 1

        super().__init__(backend, L('@QFrameAdjuster.module_title'),
                         layout=qtx.QXVBoxLayout([grid_l]) )

