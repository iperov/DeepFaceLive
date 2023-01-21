from pathlib import Path
from typing import Iterator, List, Tuple, Union

import numpy as np
from xlib import onnxruntime as lib_ort
from xlib import path as lib_path
from xlib.image import ImageProcessor
from xlib.net import ThreadFileDownloader
from xlib.onnxruntime.device import ORTDeviceInfo


class DFMModelInfo:
    def __init__(self, name : str, model_path : Path, url : str = None):
        self._name = name
        self._model_path = model_path
        self._url = url

    def get_name(self) -> str: return self._name
    def get_model_path(self) -> Path: return self._model_path
    def get_url(self) -> Union[str, None]: return self._url

    def __eq__(self, other):
        if self is not None and other is not None and isinstance(self, DFMModelInfo) and isinstance(other, DFMModelInfo):
            return self._name == other._name
        return False

    def __hash__(self):
        return self._name.__hash__()

    def __str__(self):
        return self._name


def get_available_models_info(models_path : Path) -> List[DFMModelInfo]:
    # predefined list of celebs with urls
    dfm_models = [
            DFMModelInfo(name='Albica Johns', model_path=models_path / f'Albica_Johns.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/ALBICA_JOHNS/Albica_Johns.dfm'),
            DFMModelInfo(name='Amber Song', model_path=models_path / f'Amber_Song.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/AMBER_SONG/Amber_Song.dfm'),
            DFMModelInfo(name='Ava de Addario', model_path=models_path / f'Ava_de_Addario.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/AVA_DE_ADDARIO/Ava_de_Addario.dfm'),
            DFMModelInfo(name='Bryan Greynolds', model_path=models_path / f'Bryan_Greynolds.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/BRYAN_GREYNOLDS/Bryan_Greynolds.dfm'),
            DFMModelInfo(name='David Kovalniy', model_path=models_path / f'David_Kovalniy.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/DAVID_KOVALNIY/David_Kovalniy.dfm'),
            DFMModelInfo(name='Dean Wiesel', model_path=models_path / f'Dean_Wiesel.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/DEAN_WIESEL/Dean_Wiesel.dfm'),
            DFMModelInfo(name='Dilraba Dilmurat', model_path=models_path / f'Dilraba_Dilmurat.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/DILRABA_DILMURAT/Dilraba_Dilmurat.dfm'),
            DFMModelInfo(name='Emily Winston', model_path=models_path / f'Emily_Winston.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/EMILY_WINSTON/Emily_Winston.dfm'),
            DFMModelInfo(name='Ewon Spice', model_path=models_path / f'Ewon_Spice.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/EWON_SPICE/Ewon_Spice.dfm'),
            DFMModelInfo(name='Irina Arty', model_path=models_path / f'Irina_Arty.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/IRINA_ARTY/Irina_Arty.dfm'),
            DFMModelInfo(name='Jackie Chan', model_path=models_path / f'Jackie_Chan.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/JACKIE_CHAN/Jackie_Chan.dfm'),
            DFMModelInfo(name='Jesse Stat 320', model_path=models_path / f'Jesse_Stat_320.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/JESSE_STAT/Jesse_Stat_320.dfm'),
            DFMModelInfo(name='Joker', model_path=models_path / f'Joker.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/JOKER/Joker.dfm'),
            DFMModelInfo(name='Keanu Reeves', model_path=models_path / f'Keanu_Reeves.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/KEANU_REEVES/Keanu_Reeves.dfm'),
            DFMModelInfo(name='Keanu Reeves 320', model_path=models_path / f'Keanu_Reeves_320.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/KEANU_REEVES_320/Keanu_Reeves_320.dfm'),
            DFMModelInfo(name='Kim Jarrey', model_path=models_path / f'Kim_Jarrey.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/KIM_JARREY/Kim_Jarrey.dfm'),
            DFMModelInfo(name='Liu Lice', model_path=models_path / f'Liu_Lice.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/LIU_LICE/Liu_Lice.dfm'),
            DFMModelInfo(name='Matilda Bobbie', model_path=models_path / f'Matilda_Bobbie.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/MATILDA_BOBBIE/Matilda_Bobbie.dfm'),
            DFMModelInfo(name='Meggie Merkel', model_path=models_path / f'Meggie_Merkel.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/MEGGIE_MERKEL/Meggie_Merkel.dfm'),
            DFMModelInfo(name='Millie Park', model_path=models_path / f'Millie_Park.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/MILLIE_PARK/Millie_Park.dfm'),
            DFMModelInfo(name='Mr. Bean', model_path=models_path / f'Mr_Bean.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/MR_BEAN/Mr_Bean.dfm'),
            DFMModelInfo(name='Natalie Fatman', model_path=models_path / f'Natalie_Fatman.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/NATALIE_FATMAN/Natalie_Fatman.dfm'),
            DFMModelInfo(name='Natasha Former', model_path=models_path / f'Natasha_Former.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/NATASHA_FORMER/Natasha_Former.dfm'),
            DFMModelInfo(name='Nicola Badge', model_path=models_path / f'Nicola_Badge.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/NICOLA_BADGE/Nicola_Badge.dfm'),
            DFMModelInfo(name='Rob Doe', model_path=models_path / f'Rob_Doe.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/ROB_DOE/Rob_Doe.dfm'),
            DFMModelInfo(name='Silwan Stillwone', model_path=models_path / f'Silwan_Stillwone.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/SILWAN_STILLWONE/Silwan_Stillwone.dfm'),
            DFMModelInfo(name='Tina Shift', model_path=models_path / f'Tina_Shift.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/TINA_SHIFT/Tina_Shift.dfm'),
            DFMModelInfo(name='Tim Chrys', model_path=models_path / f'Tim_Chrys.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/TIM_CHRYS/Tim_Chrys.dfm'),
            DFMModelInfo(name='Tim Norland', model_path=models_path / f'Tim_Norland.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/TIM_NORLAND/Tim_Norland.dfm'),
            DFMModelInfo(name='Yohanna Coralson', model_path=models_path / f'Yohanna_Coralson.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/YOHANNA_CORALSON/Yohanna_Coralson.dfm'),
            DFMModelInfo(name='Zahar Lupin', model_path=models_path / f'Zahar_Lupin.dfm', url=rf'https://github.com/iperov/DeepFaceLive/releases/download/ZAHAR_LUPIN/Zahar_Lupin.dfm'),
        ]

    # scan additional models in directory
    dfm_model_paths = [ celeb.get_model_path() for celeb in dfm_models]

    for dfm_path in lib_path.get_files_paths(models_path, extensions=['.dfm']):
        if dfm_path not in dfm_model_paths:
            dfm_models.append( DFMModelInfo(dfm_path.stem, model_path=dfm_path, ) )

    return dfm_models

def get_available_devices() -> List[ORTDeviceInfo]:
    """
    """
    return lib_ort.get_available_devices_info()


class DFMModel:
    def __init__(self, model_path : Path, device : ORTDeviceInfo = None):
        if device is None:
            device = lib_ort.get_cpu_device_info()
        self._model_path = model_path

        sess = self._sess = lib_ort.InferenceSession_with_device(str(model_path), device)

        inputs = sess.get_inputs()

        if len(inputs) == 0:
            raise Exception(f'Invalid model {model_path}')
        else:
            if 'in_face' not in inputs[0].name:
                raise Exception(f'Invalid model {model_path}')
            else:
                self._input_height, self._input_width = inputs[0].shape[1:3]
                self._model_type = 1
                if len(inputs) == 2:
                    if 'morph_value' not in inputs[1].name:
                        raise Exception(f'Invalid model {model_path}')
                    self._model_type = 2
                elif len(inputs) > 2:
                    raise Exception(f'Invalid model {model_path}')

    def get_model_path(self) -> Path: return self._model_path
    def get_input_res(self) -> Tuple[int, int]:
        return self._input_width, self._input_height

    def has_morph_value(self) -> bool:
        return self._model_type == 2

    def convert(self, img, morph_factor=0.75):
        """
         img    np.ndarray  HW,HWC,NHWC uint8,float32

         morph_factor   float   used if model supports it

        returns

         img        NHW3  same dtype as img
         celeb_mask NHW1  same dtype as img
         face_mask  NHW1  same dtype as img
        """

        ip = ImageProcessor(img)

        N,H,W,C = ip.get_dims()
        dtype = ip.get_dtype()

        img = ip.resize( (self._input_width,self._input_height) ).ch(3).to_ufloat32().get_image('NHWC')

        if self._model_type == 1:
            out_face_mask, out_celeb, out_celeb_mask = self._sess.run(None, {'in_face:0': img})
        elif self._model_type == 2:
            out_face_mask, out_celeb, out_celeb_mask = self._sess.run(None, {'in_face:0': img, 'morph_value:0':np.float32([morph_factor]) })

        out_celeb      = ImageProcessor(out_celeb).resize((W,H)).ch(3).to_dtype(dtype).get_image('NHWC')
        out_celeb_mask = ImageProcessor(out_celeb_mask).resize((W,H)).ch(1).to_dtype(dtype).get_image('NHWC')
        out_face_mask  = ImageProcessor(out_face_mask).resize((W,H)).ch(1).to_dtype(dtype).get_image('NHWC')

        return out_celeb, out_celeb_mask, out_face_mask



class DFMModelInitializer:
    """
    class to initialize DFMModel from DFMModelInfo

    use .process_events() to iterate initialization process with events
    """

    class Events:
        prev_status_initializing : bool = False
        prev_status_downloading  : bool = False
        prev_status_initialized  : bool = False
        prev_status_error        : bool = False

        new_status_initializing : bool = False
        new_status_downloading  : bool = False
        new_status_initialized  : bool = False
        new_status_error        : bool = False

        download_progress : float = None
        error : str = None
        dfm_model : DFMModel = None

    def __init__(self, dfm_model_info : DFMModelInfo, device : ORTDeviceInfo = None ): self._gen = self._generator(dfm_model_info, device)
    def process_events(self) -> 'DFMModelInitializer.Events': return next(self._gen)
    def _generator(self, dfm_model_info : DFMModelInfo, device : ORTDeviceInfo = None) -> Iterator['DFMModelInitializer.Events']:
        """
        Creates a generator object to initialize DFM model from provided parameters

        """

        INITIALIZING, DOWNLOADING, INITIALIZED, ERROR, = range(4)
        downloader : ThreadFileDownloader = None
        url = dfm_model_info.get_url()
        status = None
        while True:
            events = DFMModelInitializer.Events()

            new_status = status

            if status is None:
                new_status = INITIALIZING

            elif status == INITIALIZING:
                model_path = dfm_model_info.get_model_path()

                if not model_path.exists():
                    
                    if url is None:
                        new_status = ERROR
                        events.error = 'Model file is not found and URL is not defined.'
                    else:
                        downloader = ThreadFileDownloader(url=url, savepath=model_path)
                        new_status = DOWNLOADING
                else:
                    error = None
                    try:
                        dfm_model = DFMModel(model_path, device)
                    except Exception as e:
                        error = str(e)

                    if error is None:
                        new_status = INITIALIZED
                        events.dfm_model = dfm_model
                    else:
                        new_status = ERROR
                        events.error = error

            elif status == DOWNLOADING:
                error = downloader.get_error()
                if error is None:
                    progress = downloader.get_progress()
                    if progress == 100.0:
                        new_status = INITIALIZING
                    else:
                        events.download_progress = progress
                else:
                    new_status = ERROR
                    events.error = f'Unable to download {url}, error:' + error

            if new_status != status:
                events.prev_status_initializing = status == INITIALIZING
                events.prev_status_downloading  = status == DOWNLOADING
                events.prev_status_initialized  = status == INITIALIZED
                events.prev_status_error        = status == ERROR

                events.new_status_initializing = new_status == INITIALIZING
                events.new_status_downloading  = new_status == DOWNLOADING
                events.new_status_initialized  = new_status == INITIALIZED
                events.new_status_error        = new_status == ERROR
                status = new_status

            yield events

def DFMModel_from_path(model_path : Path, device : ORTDeviceInfo = None) -> DFMModel:
    """
    instantiates DFMModel
    """
    return DFMModel(model_path=model_path, device=device, __check=1)

def DFMModel_from_info(dfm_model_info : DFMModelInfo, device : ORTDeviceInfo = None) -> DFMModelInitializer:
    """
    instantiates DFMModelInitializer
    """
    return DFMModelInitializer(dfm_model_info=dfm_model_info, device=device)
