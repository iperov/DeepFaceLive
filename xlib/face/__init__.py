"""
Facelib.

Contains classes for effectively storing, manage, transfering and processing all face related data.

##### 

Faceset     
        .List[UImage]
        .List[UFaceMark]
        .List[UPerson]
        
FaceWarper   A class for face augmentation with geometric transformations.

##### META CLASSES

F* U* classes are picklable and expandable, have noneable members accessed via get/set. No properties.

E-classes are enums.
U-classes are unique, have uuid and can be saved in Faceset.

ELandmarks2D    L5
                L68
                L468
                
EMaskType       UNDEFINED, ..., ...

FRect           rectangle of the face in uniform float coordinates

FLandmarks2D    2D landmarks of the face in uniform float coordinates

FPose           pitch/yaw/roll values

UPerson - person info
    .uuid
    .name
    .age

UImage  - image
    .uuid
    .name
    .data   (H,W,C 1/3/4 ) of uint8[0..255]


UFaceMark  - face mark info referencing UImage from which the face was detected
    .uuid
    .UImage_uuid     - reference to FImage
    .UPerson_uuid    - reference to FPerson
    .FRect           
    .List[FLandmarks2D]
    .FPose
    
    .List[ (EMaskType, FImage_uuid, uni_mat) ]   - list of FMask and AffineMat to transform mask image space to UFaceMark image space
    
"""
from .ELandmarks2D import ELandmarks2D
from .EMaskType import EMaskType
from .Faceset import Faceset
from .FaceWarper import FaceWarper
from .FLandmarks2D import FLandmarks2D
from .FMask import FMask
from .FPose import FPose
from .FRect import FRect
from .UFaceMark import UFaceMark
from .UImage import UImage
from .UPerson import UPerson
