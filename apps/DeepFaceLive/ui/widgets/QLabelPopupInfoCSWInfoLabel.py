from localization import L
from xlib import qt as qtx
from xlib.mp import csw as lib_csw

from .QCSWControl import QCSWControl
from .QLabelPopupInfo import QLabelPopupInfo


class QLabelPopupInfoCSWInfoLabel(QCSWControl):
    def __init__(self, csw_info_label : lib_csw.InfoLabel.Client):
        """
        Implements lib_csw.InfoLabel control as QLabelPopupInfo
        """
        if not isinstance(csw_info_label, lib_csw.InfoLabel.Client):
            raise ValueError('csw_error must be an instance of InfoLabel.Client')

        self._csw_info_label = csw_info_label
        csw_info_label.call_on_config(self._on_csw_config)

        label_popup_info = self._label_popup_info = QLabelPopupInfo()

        super().__init__(csw_control=csw_info_label, layout=qtx.QXHBoxLayout([label_popup_info]))

    def _on_csw_state_change(self, state):
        super()._on_csw_state_change(state)
        if state == lib_csw.Control.State.DISABLED:
            self._label_popup_info.set_label(None)
            self._label_popup_info.set_popup_info(None)

    def _on_csw_config(self, cfg : lib_csw.InfoLabel.Config ):
        if cfg.info_icon:
            self._label_popup_info.set_info_icon()
        else:
            self._label_popup_info.set_label(L(cfg.label))

        self._label_popup_info.set_popup_info( '\n'.join([L(line) for line in cfg.info_lines])
                                                if cfg.info_lines is not None else None)


