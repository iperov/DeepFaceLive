from localization import L
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from xlib import qt as lib_qt

from ... import backend


class QBCFaceSwapViewer(lib_qt.QXCollapsibleSection):
    """
    """
    def __init__(self,  backed_weak_heap : backend.BackendWeakHeap,
                        bc : backend.BackendConnection,
                        preview_width=256,):
        self._preview_width = preview_width
        self._timer = lib_qt.QXTimer(interval=8, timeout=self._on_timer_8ms, start=True)

        self._backed_weak_heap = backed_weak_heap
        self._bc = bc
        self._bcd_id = None

        layered_images = self._layered_images = lib_qt.QXFixedLayeredImages(preview_width, preview_width)
        info_label = self._info_label = lib_qt.QXLabel( font=QXFontDB.get_fixedwidth_font(size=7))

        main_l = lib_qt.QXVBoxLayout([ (layered_images, Qt.AlignmentFlag.AlignCenter),
                                       (info_label, Qt.AlignmentFlag.AlignCenter),
                                     ], spacing=0)

        super().__init__(title=L('@QBCFaceSwapViewer.title'), content_layout=main_l)


    def _on_timer_8ms(self):
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

                for face_mark in bcd.get_face_mark_list():
                    face_align = face_mark.get_face_align()
                    if face_align is not None:
                        face_swap = face_align.get_face_swap()
                        if face_swap is not None:
                            face_swap_image = bcd.get_image(face_swap.get_image_name())
                            if face_swap_image is not None:
                                self._layered_images.add_image(face_swap_image)
                                h,w = face_swap_image.shape[0:2]
                                self._info_label.setText(f'{w}x{h}')
                                return

    def clear(self):
        self._layered_images.clear_images()
