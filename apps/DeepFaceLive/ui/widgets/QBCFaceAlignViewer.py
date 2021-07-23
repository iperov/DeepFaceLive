import numpy as np
from localization import L
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from resources.fonts import QXFontDB
from xlib import qt as lib_qt
from xlib.facemeta import FaceULandmarks
from xlib.python import all_is_not_None

from ... import backend


class QBCFaceAlignViewer(lib_qt.QXCollapsibleSection):
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

        super().__init__(title=L('@QBCFaceAlignViewer.title'),
                         content_layout=lib_qt.QXVBoxLayout(
                                        [ (layered_images, Qt.AlignmentFlag.AlignCenter),
                                          (info_label, Qt.AlignmentFlag.AlignCenter),
                                          ])  )

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
                        face_align_image_name = face_align.get_image_name()

                        source_to_aligned_uni_mat = face_align.get_source_to_aligned_uni_mat()

                        if all_is_not_None(face_align_image_name):
                            face_image = bcd.get_image(face_align_image_name).copy()

                            face_ulmrks = face_align.get_face_ulandmarks_by_type(FaceULandmarks.Type.LANDMARKS_2D_468)
                            if face_ulmrks is None:
                                face_ulmrks = face_align.get_face_ulandmarks_by_type(FaceULandmarks.Type.LANDMARKS_2D_68)

                            if face_ulmrks is not None:
                                lmrks_layer = np.zeros( (self._preview_width, self._preview_width, 4), dtype=np.uint8)

                                face_ulmrks.draw(lmrks_layer, (0,255,0,255))

                                face_mark_rect = face_mark.get_face_urect()
                                if face_mark_rect is not None:
                                    aligned_uni_rect = face_mark_rect.transform(source_to_aligned_uni_mat)
                                    aligned_uni_rect.draw(lmrks_layer, (0,0,255,255) )


                                self._layered_images.add_image(face_image)
                                self._layered_images.add_image(lmrks_layer)

                                h,w = face_image.shape[0:2]

                                self._info_label.setText(f'{w}x{h}')

                                return


    def clear(self):
        self._layered_images.clear_images()
