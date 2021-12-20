import threading
import time
from pathlib import Path
from typing import Any, Callable, List, Tuple, Union

import cv2
import numpy as np
import torch
import torch.autograd
import torchvision.models as tv
from localization import L, Localization
from modelhub import torch as torch_models
from xlib import math as lib_math
from xlib import torch as lib_torch
from xlib.console import diacon as dc
from xlib.torch.device import TorchDeviceInfo
from xlib.torch.optim import AdaBelief

from .TrainingDataGenerator import Data, TrainingDataGenerator


class FaceAlignerTrainerApp:
    def __init__(self, workspace_path : Path, faceset_path : Path):
        print('Initializing trainer.\n')
        print(f'Workspace path: {workspace_path}')
        print(f'Faceset path: {faceset_path}\n')

        workspace_path.mkdir(parents=True, exist_ok=True)
        self._workspace_path  = workspace_path
        self._faceset_path    = faceset_path
        self._model_data_path = workspace_path / 'model.dat'

        # system vars
        self._model_lock = threading.Lock()
        self._ev_request_reset_model = threading.Event()
        self._ev_request_preview = threading.Event()
        self._ev_request_export_model = threading.Event()
        self._ev_request_save = threading.Event()
        self._ev_request_quit = threading.Event()

        # state vars
        self._is_quit = False
        self._is_device_changed = False
        self._new_viewing_data = None
        self._is_previewing_samples = False
        self._new_preview_data : 'PreviewData' = None
        self._last_save_time = None
        self._req_is_training = None

        # settings / params
        self._model_data = None
        self._device = None
        self._device_info = None
        self._batch_size = None
        self._resolution = None
        self._learning_rate = None
        self._random_warp = None
        self._iteration = None
        self._autosave_period = None
        self._is_training = False
        self._loss_history = {}

        self._model = None
        self._model_optimizer = None

        # Generators
        self._training_generator = TrainingDataGenerator(faceset_path)

        # Load and start
        self.load()
        threading.Thread(target=self.preview_thread_proc, daemon=True).start()
        self._training_generator.set_running(True)

        self.get_main_dlg().set_current()
        self.main_loop()

        # Finalizing
        self._training_generator.stop()
        dc.Diacon.stop()

    def get_device_info(self): return self._device_info
    def set_device_info(self, device_info : TorchDeviceInfo):
        self._device = lib_torch.get_device(device_info)
        self._device_info = device_info
        self._is_device_changed = True

    def get_batch_size(self) -> int: return self._batch_size
    def set_batch_size(self, batch_size : int):
        self._batch_size = batch_size
        self._training_generator.set_batch_size(batch_size)

    def get_resolution(self) -> int: return self._resolution
    def set_resolution(self, resolution : int):
        self._resolution = resolution
        self._training_generator.set_resolution(resolution)

    def get_learning_rate(self) -> float: return self._learning_rate
    def set_learning_rate(self, learning_rate : float):
        self._learning_rate = learning_rate
        if self._model_optimizer is not None:
            self._model_optimizer.set_lr(learning_rate)

    def get_random_warp(self) -> bool: return self._random_warp
    def set_random_warp(self, random_warp : bool):
        self._random_warp = random_warp
        self._training_generator.set_random_warp(random_warp)

    def get_iteration(self) -> int: return self._iteration
    def set_iteration(self, iteration : int):
        self._iteration = iteration
        for key in self._loss_history.keys():
            self._loss_history[key] = self._loss_history[key][:iteration]

    def get_autosave_period(self): return self._autosave_period
    def set_autosave_period(self, mins : int):
        self._autosave_period = mins

    def get_is_training(self) -> bool:  return self._req_is_training if self._req_is_training is not None else self._is_training
    def set_is_training(self, training : bool):
        self._req_is_training = training

    def get_loss_history(self): return self._loss_history
    def set_loss_history(self, lh): self._loss_history = lh

    def load(self):
        self._model_data = model_data = torch.load(self._model_data_path, map_location='cpu') if self._model_data_path.exists() else {}

        self.set_device_info( lib_torch.get_device_info_by_index(model_data.get('device_index', -1)) )
        self.set_batch_size( model_data.get('batch_size', 64) )
        self.set_resolution( model_data.get('resolution', 224) )
        self.set_learning_rate( model_data.get('learning_rate', 5e-5) )
        self.set_random_warp( model_data.get('random_warp', True) )
        self.set_iteration( model_data.get('iteration', 0) )
        self.set_autosave_period( model_data.get('autosave_period', 25) )
        self.set_is_training( model_data.get('training', False) )
        self.set_loss_history ( model_data.get('loss_history', {}) )

        self.reset_model(load=True)



    def reset_model(self, load : bool = True):
        while True:
            #model = tv.mobilenet.mobilenet_v3_large(num_classes=6)
            model = torch_models.FaceAlignerNet()
            model.train()
            model.to(self._device)

            model_optimizer = AdaBelief(model.parameters(), lr=5e-5, lr_dropout=0.3)

            if load:
                model_state_dict = self._model_data.get('model_state_dict', None)
                if model_state_dict is not None:
                    try:
                        model.load_state_dict(model_state_dict)
                        model.to(self._device)

                        model_optimizer_state_dict = self._model_data.get('model_optimizer_state_dict', None)
                        if model_optimizer_state_dict is not None:
                            model_optimizer.load_state_dict(model_optimizer_state_dict)

                    except:
                        print('Network weights have been reseted.')
                        self._model_data['model_state_dict'] = None
                        self._model_data['model_optimizer_state_dict'] = None
                        continue
            else:
                print('Network weights have been reseted.')
            break

        self._model = model
        self._model_optimizer = model_optimizer

    def save(self):
        if self._model_data is not None:
            d = {'device_index' : self._device_info.get_index(),
                'batch_size' : self.get_batch_size(),
                'resolution' : self.get_resolution(),
                'random_warp' : self.get_random_warp(),
                'iteration' : self.get_iteration(),
                'autosave_period' : self.get_autosave_period(),
                'training' : self.get_is_training(),
                'loss_history' : self.get_loss_history(),
                'model_state_dict' : self._model.state_dict(),
                'model_optimizer_state_dict': self._model_optimizer.state_dict(),
                }

            torch.save(d, self._model_data_path)

    def export(self):
        self._model.to('cpu')
        self._model.eval()

        torch.onnx.export(  self._model,
                            (torch.from_numpy( np.zeros( (1,3,self._resolution,self._resolution), dtype=np.float32)),) ,
                            str(self._workspace_path / 'FaceAligner.onnx'),
                            verbose=True,
                            training=torch.onnx.TrainingMode.EVAL,
                            opset_version=12,
                            do_constant_folding=True,
                            input_names=['in'],
                            output_names=['mat'],
                            dynamic_axes={'in' : {0:'batch_size'}, 'mat' : {0:'batch_size'}}, )

        self._model.to(self._device)
        self._model.train()


    def preview_thread_proc(self):


        while not self._is_quit:
            preview_data, self._new_preview_data = self._new_preview_data, None
            if preview_data is not None:
                # new preview data to show
                data = preview_data.training_data
                n = np.random.randint(data.batch_size)
                img_aligned = data.img_aligned[n].transpose((1,2,0))
                img_aligned_shifted = data.img_aligned_shifted[n].transpose((1,2,0))

                H,W = img_aligned_shifted.shape[:2]


                shift_mat = lib_math.Affine2DUniMat(data.shift_uni_mats[n]).invert().to_exact_mat(W,H, W, H)
                shift_mat_pred = lib_math.Affine2DUniMat(preview_data.shift_uni_mats_pred[n]).invert().to_exact_mat(W,H, W, H)

                img_aligned_unshifted = cv2.warpAffine(img_aligned_shifted, shift_mat, (W,H))
                img_aligned_unshifted_pred = cv2.warpAffine(img_aligned_shifted, shift_mat_pred, (W,H))

                screen = np.concatenate([img_aligned, img_aligned_shifted, img_aligned_unshifted, img_aligned_unshifted_pred], 1)
                cv2.imshow('Preview', screen)


            viewing_data, self._new_viewing_data = self._new_viewing_data, None
            if viewing_data is not None:
                n = np.random.randint(viewing_data.batch_size)
                img_aligned_shifted = viewing_data.img_aligned_shifted[n].transpose((1,2,0))
                screen = np.concatenate([img_aligned_shifted], 1)
                cv2.imshow('Viewing samples', screen)


            cv2.waitKey(5)
            time.sleep(0.005)

    def main_loop(self):

        while not self._is_quit:

            if self._ev_request_reset_model.is_set():
                self._ev_request_reset_model.clear()
                self.reset_model(load=False)

            if self._is_device_changed:
                self._is_device_changed = False
                self._model.to(self._device)
                self._model_optimizer.load_state_dict(self._model_optimizer.state_dict())

            if self._req_is_training is not None:
                if self._req_is_training != self._is_training:
                    if self._req_is_training:
                        self._last_save_time = time.time()
                    else:
                        self._last_save_time = None
                        torch.cuda.empty_cache()
                    self._is_training = self._req_is_training
                self._req_is_training = None

            self.main_loop_training()

            if self._is_training and self._last_save_time is not None:
                while (time.time()-self._last_save_time)/60 >= self._autosave_period:
                    self._last_save_time += self._autosave_period*60
                    self._ev_request_save.set()

            if self._ev_request_export_model.is_set():
                self._ev_request_export_model.clear()
                print('Exporting...')
                self.export()
                print('Exporting done.')
                dc.Diacon.get_current_dlg().recreate().set_current()

            if self._ev_request_save.is_set():
                self._ev_request_save.clear()
                print('Saving...')
                self.save()
                print('Saving done.')
                dc.Diacon.get_current_dlg().recreate().set_current()

            if self._ev_request_quit.is_set():
                self._ev_request_quit.clear()
                self._is_quit = True

            time.sleep(0.005)

    def main_loop_training(self):
        """
        separated function, because torch tensors refences must be freed from python locals
        """
        if self._is_training or \
            self._is_previewing_samples or \
            self._ev_request_preview.is_set():

                training_data = self._training_generator.get_next_data(wait=False)
                if training_data is not None and \
                   training_data.resolution == self.get_resolution(): # Skip if resolution is different, due to delay
                    if self._is_training:
                        self._model_optimizer.zero_grad()

                    if self._ev_request_preview.is_set() or \
                        self._is_training:
                        # Inference for both preview and training
                        img_aligned_shifted_t = torch.tensor(training_data.img_aligned_shifted).to(self._device)
                        shift_uni_mats_pred_t = self._model(img_aligned_shifted_t)#.view( (-1,2,3) )

                    if self._is_training:
                        # Training optimization step
                        shift_uni_mats_t = torch.tensor(training_data.shift_uni_mats).to(self._device)
                        loss_t = (shift_uni_mats_pred_t-shift_uni_mats_t).square().mean()*10.0
                        loss_t.backward()
                        self._model_optimizer.step()
                        loss = loss_t.detach().cpu().numpy()
                        rec_loss_history = self._loss_history.get('reconstruct', None)
                        if rec_loss_history is None:
                            rec_loss_history = self._loss_history['reconstruct'] = []
                        rec_loss_history.append(float(loss))
                        self.set_iteration( self.get_iteration() + 1 )

                    if self._ev_request_preview.is_set():
                        self._ev_request_preview.clear()
                        # Preview request
                        pd = PreviewData()
                        pd.training_data = training_data
                        pd.shift_uni_mats_pred = shift_uni_mats_pred_t.detach().cpu().numpy()
                        self._new_preview_data = pd

                    if self._is_previewing_samples:
                        self._new_viewing_data = training_data

    def get_main_dlg(self):
        last_loss = 0
        rec_loss_history = self._loss_history.get('reconstruct', None)
        if rec_loss_history is not None:
            if len(rec_loss_history) != 0:
                last_loss = rec_loss_history[-1]

        return dc.DlgChoices([
                dc.DlgChoice(short_name='sgm', row_def='| Sample generator menu.',
                            on_choose=lambda dlg: self.get_sample_generator_dlg(dlg).set_current()),

                dc.DlgChoice(short_name='d', row_def=f'| Device | {self._device_info}',
                            on_choose=lambda dlg: self.get_training_device_dlg(dlg).set_current()),

                dc.DlgChoice(short_name='lr', row_def=f'| Learning rate | {self.get_learning_rate()}',
                         on_choose=lambda dlg: self.get_learning_rate_dlg(parent_dlg=dlg).set_current() ),

                dc.DlgChoice(short_name='i', row_def=f'| Iteration | {self.get_iteration()}',
                         on_choose=lambda dlg: self.get_iteration_dlg(parent_dlg=dlg).set_current() ),

                dc.DlgChoice(short_name='l', row_def=f'| Print loss history | Last loss = {last_loss:.5f} ',
                             on_choose=self.on_main_dlg_print_loss_history ),

                dc.DlgChoice(short_name='p', row_def='| Show current preview.',
                            on_choose=lambda dlg: (self._ev_request_preview.set(), dlg.recreate().set_current())),

                dc.DlgChoice(short_name='t', row_def=f'| Training | {self.get_is_training()}',
                         on_choose=lambda dlg: (self.set_is_training(not self.get_is_training()), dlg.recreate().set_current()) ),

                dc.DlgChoice(short_name='reset', row_def='| Reset model.',
                            on_choose=lambda dlg: (self._ev_request_reset_model.set(), dlg.recreate().set_current()) ),

                dc.DlgChoice(short_name='export', row_def='| Export model.',
                            on_choose=lambda dlg: self._ev_request_export_model.set() ),

                dc.DlgChoice(short_name='se', row_def=f'| Autosave period | {self.get_autosave_period()} minutes',
                            on_choose=lambda dlg: self.get_autosave_period_dlg(dlg).set_current()),

                dc.DlgChoice(short_name='s', row_def='| Save all.',
                            on_choose=lambda dlg: self._ev_request_save.set() ),

                dc.DlgChoice(short_name='q', row_def='| Quit now.',
                            on_choose=self.on_main_dlg_quit )
                ], on_recreate=lambda dlg: self.get_main_dlg(),
                top_rows_def='|c9 Main menu' )

    def on_main_dlg_quit(self, dlg):
        self._ev_request_quit.set()

    def on_main_dlg_print_loss_history(self, dlg):
        max_lines = 20
        for key in self._loss_history.keys():
            lh = self._loss_history[key]

            print(f'Loss history for: {key}')

            lh_len = len(lh)
            if lh_len >= max_lines:
                d = len(lh) // max_lines

                lh_ar = np.array(lh[-d*max_lines:], np.float32)
                lh_ar = lh_ar.reshape( (max_lines, d))
                lh_ar_max, lh_ar_min, lh_ar_mean, lh_ar_median = lh_ar.max(-1), lh_ar.min(-1), lh_ar.mean(-1), np.median(lh_ar, -1)


                print( '\n'.join( f'max:[{max_value:.5f}] min:[{min_value:.5f}] mean:[{mean_value:.5f}] median:[{median_value:.5f}]' for max_value, min_value, mean_value, median_value in zip(lh_ar_max, lh_ar_min, lh_ar_mean, lh_ar_median) ) )

        dlg.recreate().set_current()


    def get_sample_generator_dlg(self, parent_dlg):
        return dc.DlgChoices([
            dc.DlgChoice(short_name='v', row_def=f'| Previewing samples | {self._is_previewing_samples}',
                         on_choose=self.on_sample_generator_dlg_previewing_last_samples,
                         ),

            dc.DlgChoice(short_name='rw', row_def=f'| Random warp | {self.get_random_warp()}',
                         on_choose=lambda dlg: (self.set_random_warp(not self.get_random_warp()), dlg.recreate().set_current()) ),

            dc.DlgChoice(short_name='r', row_def=f'| Running | {self._training_generator.is_running()}',
                         on_choose=lambda dlg: (self._training_generator.set_running(not self._training_generator.is_running()), dlg.recreate().set_current()) ),

            ],
            on_recreate=lambda dlg: self.get_sample_generator_dlg(parent_dlg),
            on_back    =lambda dlg: parent_dlg.recreate().set_current(),
            top_rows_def='|c9 Sample generator menu' )

    def on_sample_generator_dlg_previewing_last_samples(self, dlg):
        self._is_previewing_samples = not self._is_previewing_samples
        dlg.recreate().set_current()

    def get_training_dlg(self, parent_dlg):
        return dc.DlgChoices([

            ],
            on_recreate=lambda dlg: self.get_training_dlg(parent_dlg),
            on_back    =lambda dlg: parent_dlg.recreate().set_current(),
            top_rows_def='|c9 Training menu' )

    def get_autosave_period_dlg(self, parent_dlg):
        return dc.DlgNumber(is_float=False, min_value=1,
                            on_value  = lambda dlg, value: (self.set_autosave_period(value), parent_dlg.recreate().set_current()),
                            on_recreate = lambda dlg: self.get_autosave_period_dlg(parent_dlg),
                            on_back   = lambda dlg: parent_dlg.recreate().set_current(),
                            top_rows_def='|c9 Set save every min',  )

    def get_iteration_dlg(self, parent_dlg):
        return dc.DlgNumber(is_float=False, min_value=0,
                            on_value  = lambda dlg, value: (self.set_iteration(value), parent_dlg.recreate().set_current()),
                            on_recreate = lambda dlg: self.get_iteration_dlg(parent_dlg),
                            on_back   = lambda dlg: parent_dlg.recreate().set_current(),
                            top_rows_def='|c9 Set iteration',  )

    def get_learning_rate_dlg(self, parent_dlg):
        return dc.DlgNumber(is_float=True, min_value=0, max_value=0.1,
                            on_value  = lambda dlg, value: (self.set_learning_rate(value), parent_dlg.recreate().set_current()),
                            on_recreate = lambda dlg: self.get_learning_rate_dlg(parent_dlg),
                            on_back   = lambda dlg: parent_dlg.recreate().set_current(),
                            top_rows_def='|c9 Set learning rate',  )

    def get_training_device_dlg(self, parent_dlg):
        return DlgTorchDevicesInfo(on_device_choice = lambda dlg, device_info: (self.set_device_info(device_info), parent_dlg.recreate().set_current()),
                                   on_recreate = lambda dlg: self.get_training_device_dlg(parent_dlg),
                                   on_back     = lambda dlg: parent_dlg.recreate().set_current(),
                                   top_rows_def='|c9 Choose device'
                                   )

class DlgTorchDevicesInfo(dc.DlgChoices):
    def __init__(self, on_device_choice : Callable = None,
                       on_device_multi_choice : Callable = None,
                       on_recreate = None,
                       on_back : Callable = None,
                       top_rows_def : Union[str, List[str]] = None,
                       bottom_rows_def : Union[str, List[str]] = None,):
        devices = lib_torch.get_available_devices_info()
        super().__init__(choices=[
                            dc.DlgChoice(short_name=f'{device.get_index()}' if not device.is_cpu() else 'c',
                                         row_def= f"| {str(device.get_name())} " +
                                                 (f"| {(device.get_total_memory() / 1024**3) :.3}Gb" if not device.is_cpu() else ""),
                                         on_choose= ( lambda dlg, i=i: on_device_choice(dlg, devices[i]) ) \
                                                      if on_device_choice is not None else None)
                            for i, device in enumerate(devices) ],
                         on_multi_choice=(lambda idxs: on_device_multi_choice([ devices[idx] for idx in idxs ])) \
                                          if on_device_multi_choice is not None else None,
                         on_recreate=on_recreate, on_back=on_back,
                         top_rows_def=top_rows_def, bottom_rows_def=bottom_rows_def)

class PreviewData:
    training_data : Data = None
    shift_uni_mats_pred = None