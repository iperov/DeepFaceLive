from pathlib import Path

import cv2
import numpy as np
from xlib.image import ImageProcessor
from xlib.file import SplittedFile

class FaceMarkerLBF:
    def __init__(self):
        path = Path(__file__).parent / 'lbfmodel.yaml'
        SplittedFile.merge(path, delete_parts=False)
        
        marker = self.marker = cv2.face.createFacemarkLBF()
        marker.loadModel(str(path))

    def extract(self, img : np.ndarray):
        """
        arguments

         img    np.ndarray  HW,HWC,NHWC

        returns

         [N,68,2]
        """
        ip = ImageProcessor(img)

        N,H,W,_ = ip.get_dims()

        feed_img = ip.to_grayscale().to_uint8().get_image('NHWC')

        lmrks_list = []
        for n in range( max(1,N) ):
            _, lmrks = self.marker.fit(feed_img[n], np.array([ [0,0,W,H] ]) )
            lmrks = lmrks[0][0]

            lmrks_list.append(lmrks)

        return np.float32(lmrks_list)


