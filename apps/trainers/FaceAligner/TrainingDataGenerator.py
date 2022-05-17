import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, List, Tuple, Union

import cv2
import numpy as np
from xlib import face as lib_face
from xlib import image as lib_img
from xlib import mp as lib_mp
from xlib import mt as lib_mt
from xlib.image import sd as lib_sd


class Data:
    def __init__(self):
        self.batch_size : int = None
        self.resolution : int = None
        self.img_aligned : np.ndarray = None
        self.img_aligned_shifted : np.ndarray = None
        self.shift_uni_mats : np.ndarray = None

class TrainingDataGenerator(lib_mp.MPWorker):
    def __init__(self, faceset_path : Path):
        faceset_path = Path(faceset_path)
        if not faceset_path.exists():
            raise Exception (f'{faceset_path} does not exist.')

        super().__init__(sub_args=[faceset_path])
        
        self._datas = [ deque() for _ in range(self.get_process_count())]
        self._datas_counter = 0
        self._running = False

    def get_next_data(self, wait : bool) -> Union[Data, None]:
        """
        wait and returns new generated data
        """
        while True:
            for _ in range(self.get_process_count()):
                process_id, self._datas_counter = self._datas_counter % len(self._datas), self._datas_counter + 1
                data = self._datas[process_id]
                
                if len(data) != 0:
                    self._send_msg('data_received', process_id=process_id)
                    return data.popleft()
                    
            if not wait:
                return None
            time.sleep(0.005)

    def is_running(self) -> bool: return self._running
    def set_running(self, running : bool):
        self._running = running
        self._send_msg('running', running)

    def set_batch_size(self, batch_size):
        self._send_msg('batch_size', batch_size)

    def set_resolution(self, resolution):
        self._send_msg('resolution', resolution)
        
    def set_random_warp(self, random_warp):
        self._send_msg('random_warp', random_warp)

    ###### IMPL HOST
    def _on_host_sub_message(self, process_id, name, *args, **kwargs):
        """
        message from sub
        """
        if name == 'data':
            self._datas[process_id].append(args[0])

    ###### IMPL SUB
    def _on_sub_initialize(self, faceset_path : Path):
        self._fs = fs = lib_face.Faceset(faceset_path)
        self._ufm_uuids = fs.get_all_UFaceMark_uuids()
        self._ufm_uuid_indexes = []
        self._sent_buffers_count = 0
        self._running = False
        self._batch_size = None
        self._resolution = None
        self._random_warp = None
        
        self._n_batch = 0
        self._img_aligned_list = []
        self._img_aligned_shifted_list = []
        self._shift_mat_list = []
    
    def _on_sub_finalize(self):
        self._fs.close()
        
    def _on_sub_host_message(self, name, *args, **kwargs):
        """
        a message from host
        """
        if name == 'data_received':
            self._sent_buffers_count -= 1
        elif name == 'batch_size':
            self._batch_size, = args
        elif name == 'resolution':
            self._resolution, = args
        elif name == 'random_warp':
            self._random_warp, = args
        elif name == 'running':
            self._running , = args

    ####### IMPL SUB THREAD
    def _on_sub_tick(self, process_id):
        running = self._running
        if running:
            if self._batch_size is None:
                print('Unable to start TrainingGenerator: batch_size must be set')
                running = False                
            if self._resolution is None:
                print('Unable to start TrainingGenerator: resolution must be set')
                running = False
            if self._random_warp is None:
                print('Unable to start TrainingGenerator: random_warp must be set')
                running = False
                
        if running:        
            if self._sent_buffers_count < 2:
                batch_size = self._batch_size
                resolution = self._resolution
                face_coverage = 1.0

                rw_grid_cell_range = [3,7]
                rw_grid_rot_deg_range = [-180,180]
                rw_grid_scale_range = [-0.25, 2.5]
                rw_grid_tx_range = [-0.50, 0.50]
                rw_grid_ty_range = [-0.50, 0.50]

                align_rot_deg_range = [-180,180]
                align_scale_range = [0.0,2.5]
                align_tx_range = [-0.50, 0.50]
                align_ty_range = [-0.50, 0.50]
                
                
                
                random_mask_complexity = 3
                sharpen_chance = 25
                motion_blur_chance = 25
                gaussian_blur_chance = 25
                reresize_chance = 25
                recompress_chance = 25

                img_aligned_list = []
                img_aligned_shifted_list = []
                shift_mat_list = []
                
                if self._n_batch < batch_size:
                    # Make only 1 sample per tick 
                    while True:
                        uuid1 = self._get_next_UFaceMark_uuid()

                        ufm1 = self._fs.get_UFaceMark_by_uuid(uuid1)

                        flmrks1 = ufm1.get_FLandmarks2D_best()
                        if flmrks1 is None:
                            print(f'Corrupted faceset, no FLandmarks2D for UFaceMark {ufm1.get_uuid()}')
                            continue

                        uimg1 = self._fs.get_UImage_by_uuid(ufm1.get_UImage_uuid())
                        if uimg1 is None:
                            print(f'Corrupted faceset, no UImage for UFaceMark {ufm1.get_uuid()}')
                            continue

                        img1 = uimg1.get_image()

                        if img1 is None:
                            print(f'Corrupted faceset, no image in UImage {uimg1.get_uuid()}')
                            continue
                        
                        img_aligned, _ = flmrks1.cut(img1, face_coverage, resolution)
                        img_aligned = img_aligned.astype(np.float32) / 255.0
                        
                        _, img_to_face_uni_mat1  = flmrks1.calc_cut( img1.shape[0:2], face_coverage, resolution)
                        

                        fw1 = lib_face.FaceWarper(img_to_face_uni_mat1,
                                                  align_rot_deg=align_rot_deg_range,
                                                  align_scale=align_scale_range,
                                                  align_tx=align_tx_range,
                                                  align_ty=align_ty_range,
                                                  rw_grid_cell_count=rw_grid_cell_range,
                                                  rw_grid_rot_deg=rw_grid_rot_deg_range,
                                                  rw_grid_scale=rw_grid_scale_range,
                                                  rw_grid_tx=rw_grid_tx_range,
                                                  rw_grid_ty=rw_grid_ty_range,
                                                )
                       
                        img_aligned_shifted = fw1.transform(img1, resolution, random_warp=self._random_warp).astype(np.float32) / 255.0
    
                        ip = lib_img.ImageProcessor(img_aligned_shifted)
                        rnd = np.random
                        if rnd.randint(2) == 0:
                            ip.hsv( rnd.uniform(0,1), rnd.uniform(-0.5,0.5), rnd.uniform(-0.5,0.5), mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity))
                        else:
                            ip.levels( [ [rnd.uniform(0,0.25),rnd.uniform(0.75,1.0),rnd.uniform(0.5,1.5), rnd.uniform(0,0.25),rnd.uniform(0.75,1.0),  ],
                                         [rnd.uniform(0,0.25),rnd.uniform(0.75,1.0),rnd.uniform(0.5,1.5), rnd.uniform(0,0.25),rnd.uniform(0.75,1.0),],
                                         [rnd.uniform(0,0.25),rnd.uniform(0.75,1.0),rnd.uniform(0.5,1.5), rnd.uniform(0,0.25),rnd.uniform(0.75,1.0),], ], mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity))
                        
                        if rnd.randint(2) == 0:
                            if rnd.randint(100) < sharpen_chance:
                                if rnd.randint(2) == 0:
                                    ip.box_sharpen(size=rnd.randint(1,11), power=rnd.uniform(0.5,5.0), mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity) )
                                else:
                                    ip.gaussian_sharpen(sigma=1.0, power=rnd.uniform(0.5,5.0), mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity) )
                                    
                        else:            
                            if rnd.randint(100) < motion_blur_chance:
                                ip.motion_blur (size=rnd.randint(1,11), angle=rnd.randint(360), mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity))
                            if rnd.randint(100) < gaussian_blur_chance:
                                ip.gaussian_blur (sigma=rnd.uniform(0.5,3.0), mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity))

                        if np.random.randint(2) == 0:
                            if rnd.randint(100) < reresize_chance:
                                ip.reresize( rnd.uniform(0.0,0.75), interpolation=ip.Interpolation.NEAREST, mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity) )
                        if np.random.randint(2) == 0:
                            if rnd.randint(100) < reresize_chance:
                                ip.reresize( rnd.uniform(0.0,0.75), interpolation=ip.Interpolation.LINEAR, mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity) )
                        if rnd.randint(100) < recompress_chance:
                            ip.jpeg_recompress(quality=rnd.randint(10,75), mask=lib_sd.random_circle_faded_multi((resolution,resolution), complexity=random_mask_complexity) )
                        
                        img_aligned_shifted = ip.get_image('HWC')
                        
                        self._img_aligned_list.append(img_aligned)
                        self._img_aligned_shifted_list.append(img_aligned_shifted)
                        self._shift_mat_list.append( fw1.get_aligned_random_transform_mat() )
                        self._n_batch += 1
                        break
                    
                if self._n_batch == batch_size:
                    data = Data()
                    data.batch_size = batch_size
                    data.resolution = resolution
                    data.img_aligned = np.array(self._img_aligned_list).transpose( (0,3,1,2))
                    data.img_aligned_shifted = np.array(self._img_aligned_shifted_list).transpose( (0,3,1,2))
                    data.shift_uni_mats = np.array(self._shift_mat_list)

                    self._send_msg('data', data)
                    self._sent_buffers_count +=1
                    
                    self._n_batch = 0
                    self._img_aligned_list = []
                    self._img_aligned_shifted_list = []
                    self._shift_mat_list = []


    def _get_next_UFaceMark_uuid(self) -> bytes:
        if len(self._ufm_uuid_indexes) == 0:
            self._ufm_uuid_indexes = [*range(len(self._ufm_uuids))]
            np.random.shuffle(self._ufm_uuid_indexes)
        idx = self._ufm_uuid_indexes.pop()
        return self._ufm_uuids[idx]
