from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx

from ... import backend


class QBCFaceSwapViewer(qtx.QXCollapsibleSection):
    """
    """
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

        main_l = qtx.QXVBoxLayout([ (layered_images, qtx.AlignCenter),
                                    (info_label, qtx.AlignCenter) ])

        super().__init__(title=L('@QBCFaceSwapViewer.title'), content_layout=main_l)


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
                    face_swap_image = bcd.get_image(fsi.face_swap_image_name)
                    if face_swap_image is not None:
                        self._layered_images.add_image(face_swap_image)
                        h,w = face_swap_image.shape[0:2]
                        self._info_label.setText(f'{w}x{h}')
                        return

    def clear(self):
        self._layered_images.clear_images()
