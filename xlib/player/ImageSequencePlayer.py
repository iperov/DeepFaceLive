from pathlib import Path
from typing import Tuple

import numpy as np
from .. import cv as lib_cv
from .. import path as lib_path

from .FramePlayer import FramePlayer


class ImageSequencePlayer(FramePlayer):
    """
    Play image sequence folder.

    arguments

        dir_path       path to directory

        is_realtime(True)    bool   False - process every frame as fast as possible
                                            fps parameter will be ignored
                                    True  - process in real time with desired fps

        is_autorewind(True)  bool

        fps                 float   specify fps

        target_width(None)  int     if None : resolution will be not modified

    raises

        Exception   path does not exists
                    path has no image files
    """
    SUPPORTED_IMAGE_SEQUENCE_SUFFIXES = ['.jpg','.png']

    def __init__(self, dir_path,
                        on_error_func=None,
                        on_player_state_func=None,
                        on_frame_update_func=None):

        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise Exception(f'{dir_path} does not exist.')

        if not dir_path.is_dir():
            raise Exception(f'{dir_path} is not a directory.')

        images_paths = lib_path.get_files_paths(dir_path, ImageSequencePlayer.SUPPORTED_IMAGE_SEQUENCE_SUFFIXES)
        if len(images_paths) == 0:
            raise Exception(f'Images with extensions {ImageSequencePlayer.SUPPORTED_IMAGE_SEQUENCE_SUFFIXES} are not found in directory: /{dir_path.name}/')

        #
        super().__init__(default_fps=30, frame_count=len(images_paths) )

        self._images_paths = images_paths
        self._dir_path = dir_path


    def _on_get_frame(self, idx) -> Tuple[np.ndarray, str]:
        filepath = self._images_paths[idx]

        try:
            img = lib_cv.imread(filepath)
            return img, filepath.name
        except Exception as e:
            return None, 'cv2.imread error: '+str(e)



