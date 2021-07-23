import os
import platform

# onnxruntime==1.8.0 requires CUDA_PATH_V11_2, but 1.8.1 don't
# keep the code if they return that behaviour
# if __name__ == '__main__':
#     if platform.system() == 'Windows':
#         if 'CUDA_PATH' not in os.environ:
#             raise Exception('CUDA_PATH should be set to environ')
#         # set environ for onnxruntime
#         # os.environ['CUDA_PATH_V11_2'] = os.environ['CUDA_PATH']

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser( "run", help="Run the application.")

    run_subparsers = run_parser.add_subparsers()

    def run_DeepFaceLive(args):
        userdata_path = Path(args.userdata_dir)
        print('Running DeepFaceLive.')
        from apps.DeepFaceLive.DeepFaceLiveApp import DeepFaceLiveApp
        DeepFaceLiveApp(userdata_path=userdata_path).run()

    p = run_subparsers.add_parser('DeepFaceLive')
    p.add_argument('--userdata-dir', default=None, action=fixPathAction, help="Workspace directory.")
    p.set_defaults(func=run_DeepFaceLive)

    def bad_args(arguments):
        parser.print_help()
        exit(0)
    parser.set_defaults(func=bad_args)

    args = parser.parse_args()
    args.func(args)

class fixPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


# from xlib import time as lib_time
# import numpy as np
# import cv2
# import cupy as cp
# import cupyx.scipy.ndimage
# import scipy
# import scipy.ndimage

# from typing import Union, Tuple

# from xlib.image import ImageProcessor

# mat = def_mat = np.array([[ 8.5966533e-01,  8.3356246e-02, 1.9525000e+02 ],#
#                           [-8.3356142e-02,  8.5966533e-01, 8.8052826e+01 ]], np.float32)#
        
# is_cp = False
# while True:
#     print('is_cp : ', is_cp)
#     img = cv2.imread(r'D:\DevelopPython\test\00000.png')
#     if is_cp:
#         img = cp.asarray(img)
#     is_cp = not is_cp
    
#     ip = ImageProcessor(img)
#     ip.sharpen(factor=10.0)
#     #ip.degrade_resize( np.random.rand() )


#     #ip.erode_blur(50, 50, fade_to_border=False)
#     #ip.resize( (500,500) )
#     #ip.warpAffine(mat, 1920, 1080)
#     x = ip.get_image('HWC')

#     x = cp.asnumpy(x)
#     cv2.imshow('', x )
#     cv2.waitKey(0) 
# import code
# code.interact(local=dict(globals(), **locals()))



if __name__ == '__main__':
    main()


# import code
# code.interact(local=dict(globals(), **locals()))
