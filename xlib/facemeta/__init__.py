"""
facemeta

Trying to standartize face description.

It is not perfect structure, but enough for current tasks.

FaceURect and FaceULandmarks mean uniform coordinates in order to apply them to any resolution.

Overall structure:

FaceMark - (mean single face data referencing any image)
           .image_name       - image reference
           .person_name      - optional name of person
           .FaceURect        - a rectangle of the face in source image space
           .list[FaceULandmarks] - a list of unique types of landmarks of the face in source image space
                                    types:
                                        LANDMARKS_5
                                        LANDMARKS_68
                                        LANDMARKS_468
           
           .FaceAlign -  an aligned face from FaceMark
           
                        .image_name         - image reference
                        .person_name        - optional name of person
                        .coverage           - coverage value used to align
                        
                        .source_source_face_ulandmarks_type     - type of FaceULandmarks from which this FaceAlign was produced
                        .source_to_aligned_uni_mat   - uniform AffineMat to FaceMark image space to FaceAlign image space
                        
                        .FaceURect               - a rectangle of the face in aligned image space
                        .list[FaceULandmarks]    - a list of unique types of landmarks of the face in aligned image space
                        
                        .FaceMask  - grayscale image to mask the face in FaceAlign image space
                                     .image_name        - image reference
                        
                        .FaceSwap  - face image of other person in the same as FaceAlign image space
                                     .image_name        - image reference
                                     .person_name       - optional name of person
                                     
                                     .FaceMask - grayscale image to mask the swapped face in FaceSwap image space
                                                 .image_name


"""

from .face import FaceMark, FaceAlign, FaceSwap, FaceMask, FaceURect, FaceULandmarks, FacePose
from .Faceset import Faceset
