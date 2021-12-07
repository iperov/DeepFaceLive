import numpy as np
from localization import L
from resources.fonts import QXFontDB
from xlib import image as lib_image
from xlib import qt as qtx

from ... import backend


class QBCMergedFrameViewer(qtx.QXCollapsibleSection):
    def __init__(self,  backed_weak_heap : backend.BackendWeakHeap,
                        bc : backend.BackendConnection,
                        preview_width=256):
        self._timer = qtx.QXTimer(interval=16, timeout=self._on_timer_16ms, start=True)

        self._backed_weak_heap = backed_weak_heap
        self._bc = bc
        self._bcd_id = None

        layered_images = self._layered_images = qtx.QXFixedLayeredImages(preview_width, preview_width)

        info_label = self._info_label = qtx.QXLabel( font=QXFontDB.get_fixedwidth_font(size=7))

        main_l = qtx.QXVBoxLayout([ (layered_images, qtx.AlignCenter),
                                    (info_label, qtx.AlignCenter) ])

        super().__init__(title=L('@QBCMergedFrameViewer.title'), content_layout=main_l)

    def _on_timer_16ms(self):
        top_qx = self.get_top_QXWindow()
        if not self.is_opened() or (top_qx is not None and top_qx.is_minimized() ):
            return

        bcd_id = self._bc.get_write_id()
        if self._bcd_id != bcd_id:
            # Has new bcd version
            bcd, self._bcd_id = self._bc.get_by_id(bcd_id), bcd_id
            if bcd is not None:
                bcd.assign_weak_heap(self._backed_weak_heap)

                self._layered_images.clear_images()

                merged_image_name = bcd.get_merged_image_name()
                merged_image = bcd.get_image(merged_image_name)

                if merged_image is not None:
                    if merged_image.dtype != np.uint8:
                        merged_image = lib_image.ImageProcessor(merged_image).to_uint8().get_image('HWC')

                    self._layered_images.add_image(merged_image)
                    h,w = merged_image.shape[0:2]
                    self._info_label.setText(f'{merged_image_name} {w}x{h}')


    def clear(self):
        self._layered_images.clear_images()
