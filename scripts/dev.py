from pathlib import Path

import numpy as np
from xlib import console as lib_con
from xlib import face as lib_face
from xlib import path as lib_path
from xlib.file import SplittedFile
from xlib import cv as lib_cv

repo_root = Path(__file__).parent.parent
large_files_list = [ (repo_root / 'modelhub' / 'onnx' / 'S3FD' / 'S3FD.onnx', 48*1024*1024),
                     (repo_root / 'modelhub' / 'onnx' / 'LIA' / 'generator.onnx', 48*1024*1024),
                     (repo_root / 'modelhub' / 'torch' / 'S3FD' / 'S3FD.pth', 48*1024*1024),
                     (repo_root / 'modelhub' / 'cv' / 'FaceMarkerLBF' / 'lbfmodel.yaml', 34*1024*1024),
                    ]

def merge_large_files(delete_parts=False):
    for filepath, _ in large_files_list:
        print(f'Merging {filepath}...')
        SplittedFile.merge(filepath, delete_parts=delete_parts)
    print('Done')

def split_large_files(delete_original=False):
    for filepath, part_size in large_files_list:
        print(f'Splitting {filepath}...')
        if filepath.exists():
            SplittedFile.split(filepath, part_size=part_size, delete_original=delete_original)
        else:
            print(f'{filepath} not found. Skipping.')

    print('Done')

def extract_FaceSynthetics(inputdir_path : Path, faceset_path : Path):
    """
    extract FaceSynthetics dataset https://github.com/microsoft/FaceSynthetics

    BACKGROUND = 0
    SKIN = 1
    NOSE = 2
    RIGHT_EYE = 3
    LEFT_EYE = 4
    RIGHT_BROW = 5
    LEFT_BROW = 6
    RIGHT_EAR = 7
    LEFT_EAR = 8
    MOUTH_INTERIOR = 9
    TOP_LIP = 10
    BOTTOM_LIP = 11
    NECK = 12
    HAIR = 13
    BEARD = 14
    CLOTHING = 15
    GLASSES = 16
    HEADWEAR = 17
    FACEWEAR = 18
    IGNORE = 255
    """
    if faceset_path.suffix != '.dfs':
        raise ValueError('faceset_path must have .dfs extension.')

    filepaths = lib_path.get_files_paths(inputdir_path)
    fs = lib_face.Faceset(faceset_path, write_access=True, recreate=True)
    for filepath in lib_con.progress_bar_iterator(filepaths, desc='Processing'):
        if filepath.suffix == '.txt':

            image_filepath = filepath.parent / f'{filepath.name.split("_")[0]}.png'
            if not image_filepath.exists():
                print(f'{image_filepath} does not exist, skipping')


            img = lib_cv.imread(image_filepath)
            H,W,C = img.shape

            lmrks = []
            for lmrk_line in filepath.read_text().split('\n'):
                if len(lmrk_line) == 0:
                    continue

                x, y = lmrk_line.split(' ')
                x, y = float(x), float(y)

                lmrks.append( (x,y) )

            lmrks = np.array(lmrks[:68], np.float32) / (H,W)

            flmrks = lib_face.FLandmarks2D.create(lib_face.ELandmarks2D.L68, lmrks)

            uimg = lib_face.UImage()
            uimg.assign_image(img)
            uimg.set_name(image_filepath.stem)

            ufm = lib_face.UFaceMark()
            ufm.set_UImage_uuid(uimg.get_uuid())
            ufm.set_FRect(flmrks.get_FRect())
            ufm.add_FLandmarks2D(flmrks)

            fs.add_UFaceMark(ufm)
            fs.add_UImage(uimg, format='png')

    fs.optimize()
    fs.close()

# seg_filepath = input_path / ( Path(image_filepath).stem + '_seg.png')
# if not seg_filepath.exists():
#     raise ValueError(f'{seg_filepath} does not exist')

# erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
# img_seg = lib_cv.imread(seg_filepath)
# if img_seg.ndim == 2:
#     img_seg = img_seg[...,None]
# if img_seg.shape[-1] != 1:
#     raise Exception(f'{seg_filepath} wrong mask file. Must be 1 channel.')

# seg_hair = img_seg.copy()

# seg_hair_inds = np.isin(img_seg, [13])
# seg_hair[~seg_hair_inds] = 0
# seg_hair[seg_hair_inds] = 255

# cv2.imshow('', img)
# cv2.waitKey(0)

# cv2.imshow('', seg_hair)
# cv2.waitKey(0)

# # fix 1-3 pix hair holes
# seg_hair = cv2.dilate(seg_hair, erode_kernel, iterations=3)
# seg_hair = cv2.erode(seg_hair, erode_kernel, iterations=3)

# cv2.imshow('', seg_hair)
# cv2.waitKey(0)
# img_seg_inds = np.isin(img_seg, [1,2,3,4,5,6,9,10,11,14])
# img_seg[~img_seg_inds] = 0
# img_seg[img_seg_inds] = 255
# import numpy as np
# import cv2
#
# from xlib import math as lib_math

# fs1 = lib_face.Faceset(r'D:\\1.dfs')
# fs1.clear_db()

# uimg = lib_face.UImage()
# uimg.assign_image( np.random.uniform(0, 255, size=(128,128,1) ).astype(np.uint8) )

# fs1.add_UImage(uimg, format='jp2', quality=30)

# uimg.assign_image( np.ones( shape=(128,128,1) ).astype(np.uint8) )

# #fs1.add_UImage(uimg, format='jp2', quality=30)


# up = lib_face.UPerson()
# up.set_name('Man')
# up.set_age(13)

# fs1.add_UPerson(up)

# ufm = lib_face.UFaceMark()
# ufm.set_UPerson_uuid(up.get_uuid())
# ufm.set_UImage_uuid(uimg.get_uuid())
# ufm.add_mask_info( lib_face.EMaskType.UNDEFINED, uimg.get_uuid(), lib_math.Affine2DUniMat.identity() )

# fs1.add_UFaceMark(ufm)

# fs1.close()


# fs = lib_face.Faceset(r'D:\\1.dfs')
# for uperson in fs.iter_UPerson():
#     print(uperson)

# for ufm in fs.iter_UFaceMark():
#     print(ufm)

# for uimg in fs.iter_UImage():
#     cv2.imshow('', uimg.get_image())
#     cv2.waitKey(0)
#     print(uimg)

# import code
# code.interact(local=dict(globals(), **locals()))


# uimg2 = lib_face.UImage()
# uimg2.assign_image( np.random.uniform(0, 255, size=(128,128,1) ).astype(np.uint8) )

# ufm = lib_face.UFaceMark()
# ufm.set_UImage_uuid(uimg.get_uuid())


# fs.add_UFaceMark(ufm)

# fs.add_UImage(uimg, format='jp2', quality=30)
# fs.add_UImage(uimg2, format='jpg', quality=10)

# #print(fs.get_fimage_count())

# print( fs.get_UFaceMark_count() )
# import code
# code.interact(local=dict(globals(), **locals()))

