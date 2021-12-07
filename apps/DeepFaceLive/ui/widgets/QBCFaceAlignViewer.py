import numpy as np
from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx

from ... import backend


class QBCFaceAlignViewer(qtx.QXCollapsibleSection):
    def __init__(self,  backed_weak_heap : backend.BackendWeakHeap,
                        bc : backend.BackendConnection,
                        preview_width=256,):

        self._preview_width = preview_width
        self._timer = qtx.QXTimer(interval=16, timeout=self._on_timer_16ms, start=True)
        self._backed_weak_heap = backed_weak_heap
        self._bc = bc
        self._bcd_id = None

        layered_images = self._layered_images = qtx.QXFixedLayeredImages(preview_width, preview_width)
        info_label = self._info_label = qtx.QXLabel( font=QXFontDB.get_fixedwidth_font(size=7))

        super().__init__(title=L('@QBCFaceAlignViewer.title'),
                         content_layout=qtx.QXVBoxLayout([(layered_images, qtx.AlignCenter),
                                                          (info_label, qtx.AlignCenter)])  )

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

                for fsi in bcd.get_face_swap_info_list():
                    face_image = bcd.get_image (fsi.face_align_image_name)
                    if face_image is not None:
                        h,w = face_image.shape[:2]
                        self._layered_images.add_image(face_image)

                        if fsi.face_align_ulmrks is not None:
                            lmrks_layer = np.zeros( (self._preview_width, self._preview_width, 4), dtype=np.uint8)

                            fsi.face_align_ulmrks.draw(lmrks_layer, (0,255,0,255))

                            if fsi.face_urect is not None and fsi.image_to_align_uni_mat is not None:
                                aligned_uni_rect = fsi.face_urect.transform(fsi.image_to_align_uni_mat)
                                aligned_uni_rect.draw(lmrks_layer, (0,0,255,255) )

                            self._layered_images.add_image(lmrks_layer)

                            self._info_label.setText(f'{w}x{h}')
                            return


    def clear(self):
        self._layered_images.clear_images()
