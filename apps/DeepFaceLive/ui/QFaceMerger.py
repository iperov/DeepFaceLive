from localization import L
from xlib import qt as qtx

from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QComboBoxCSWDynamicSingleSwitch import \
    QComboBoxCSWDynamicSingleSwitch
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QSliderCSWNumber import QSliderCSWNumber
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber


class QFaceMerger(QBackendPanel):
    def __init__(self, backend):
        cs = backend.get_control_sheet()

        q_device_label = QLabelPopupInfo(label=L('@common.device'), popup_info_text=L('@common.help.device'))
        q_device       = QComboBoxCSWDynamicSingleSwitch(cs.device, reflect_state_widgets=[q_device_label])

        q_face_x_offset_label = QLabelPopupInfo(label=L('@QFaceMerger.face_x_offset'))
        q_face_x_offset       = QSpinBoxCSWNumber(cs.face_x_offset, reflect_state_widgets=[q_face_x_offset_label])

        q_face_y_offset_label = QLabelPopupInfo(label=L('@QFaceMerger.face_y_offset'))
        q_face_y_offset       = QSpinBoxCSWNumber(cs.face_y_offset, reflect_state_widgets=[q_face_y_offset_label])

        q_face_scale_label = QLabelPopupInfo(label=L('@QFaceMerger.face_scale') )
        q_face_scale       = QSpinBoxCSWNumber(cs.face_scale, reflect_state_widgets=[q_face_scale_label])

        q_face_mask_type_label = QLabelPopupInfo(label=L('@QFaceMerger.face_mask_type') )
        q_face_mask_source_label = QLabelPopupInfo(label='SRC')
        q_face_mask_source       = QCheckBoxCSWFlag(cs.face_mask_source, reflect_state_widgets=[q_face_mask_type_label, q_face_mask_source_label])
        q_face_mask_celeb_label  = QLabelPopupInfo(label='CELEB')
        q_face_mask_celeb        = QCheckBoxCSWFlag(cs.face_mask_celeb, reflect_state_widgets=[q_face_mask_celeb_label, q_face_mask_source_label])
        q_face_mask_lmrks_label  = QLabelPopupInfo(label='LMRKS')
        q_face_mask_lmrks        = QCheckBoxCSWFlag(cs.face_mask_lmrks, reflect_state_widgets=[q_face_mask_lmrks_label, q_face_mask_source_label])

        q_face_mask_erode_label = QLabelPopupInfo(label=L('@QFaceMerger.face_mask_erode') )
        q_face_mask_erode       = QSpinBoxCSWNumber(cs.face_mask_erode, reflect_state_widgets=[q_face_mask_erode_label])

        q_face_mask_blur_label = QLabelPopupInfo(label=L('@QFaceMerger.face_mask_blur') )
        q_face_mask_blur       = QSpinBoxCSWNumber(cs.face_mask_blur, reflect_state_widgets=[q_face_mask_blur_label])

        q_color_transfer_label = QLabelPopupInfo(label=L('@QFaceMerger.color_transfer'), popup_info_text=L('@QFaceMerger.help.color_transfer'))
        q_color_transfer       = QComboBoxCSWDynamicSingleSwitch(cs.color_transfer, reflect_state_widgets=[q_color_transfer_label])

        q_interpolation_label = QLabelPopupInfo(label=L('@QFaceMerger.interpolation') )
        q_interpolation       = QComboBoxCSWDynamicSingleSwitch(cs.interpolation, reflect_state_widgets=[q_interpolation_label])

        q_color_compression_label = QLabelPopupInfo(label=L('@QFaceMerger.color_compression') )
        q_color_compression       = QSliderCSWNumber(cs.color_compression, reflect_state_widgets=[q_color_compression_label])

        q_face_opacity_label = QLabelPopupInfo(label=L('@QFaceMerger.face_opacity') )
        q_face_opacity       = QSliderCSWNumber(cs.face_opacity, reflect_state_widgets=[q_face_opacity_label])

        grid_l = qtx.QXGridLayout(spacing=5)
        row = 0
        grid_l.addWidget(q_device_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_device, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addLayout( qtx.QXVBoxLayout([q_face_x_offset_label, q_face_y_offset_label]), row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addLayout( qtx.QXHBoxLayout([q_face_x_offset, q_face_y_offset]), row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_face_scale_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_face_scale, row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget( q_face_mask_type_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addLayout( qtx.QXHBoxLayout([q_face_mask_source, q_face_mask_source_label, 5,
                                            q_face_mask_celeb, q_face_mask_celeb_label, 5,
                                            q_face_mask_lmrks, q_face_mask_lmrks_label]), row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addLayout(qtx.QXVBoxLayout([q_face_mask_erode_label,q_face_mask_blur_label]), row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addLayout(qtx.QXHBoxLayout([q_face_mask_erode,q_face_mask_blur], spacing=3), row, 1, alignment=qtx.AlignLeft )
        row += 1
        grid_l.addWidget(q_color_transfer_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_color_transfer, row, 1 )
        row += 1
        grid_l.addWidget(q_interpolation_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_interpolation, row, 1)
        row += 1
        grid_l.addWidget(q_color_compression_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_color_compression, row, 1)
        row += 1
        grid_l.addWidget(q_face_opacity_label, row, 0, alignment=qtx.AlignRight | qtx.AlignVCenter)
        grid_l.addWidget(q_face_opacity, row, 1)
        row += 1

        super().__init__(backend, L('@QFaceMerger.module_title'),
                         layout=qtx.QXVBoxLayout([grid_l]) )

