import os
from typing import Union

def L(s : Union[str, None]) -> Union[str, None]:
    return Localization.localize(s)

class Localization:
    lang = os.environ.get('__APP_LANGUAGE', 'en-US')
    allowed_langs = ['en-US', 'ru-RU', 'zh-CN']

    @staticmethod
    def set_language(lang : str = None):
        if lang not in Localization.allowed_langs:
            raise Exception(f'{lang} not in allowed languages: {Localization.allowed_langs}')
        Localization.lang = lang
        os.environ['__APP_LANGUAGE'] = lang

    @staticmethod
    def localize(s : Union[str, None]) -> Union[str, None]:
        if s is None:
            return None

        if len(s) > 0 and s[0] == '@':
            x = Localization._id_to_string_dict.get(s[1:], None)
            if x is not None:
                return x[Localization.lang]
            else:
                print(f'Localization for {s} not found.')
        return s

    _id_to_string_dict = \
    {
    'misc.auto':{
                'en-US' : 'auto',
                'ru-RU' : 'авто',
                'zh-CN' : '--'},

    'misc.menu_select':{
                'en-US' : '--select--',
                'ru-RU' : '--выбрать--',
                'zh-CN' : '--'},

    'QBackendPanel.start':{
                'en-US' : 'Start',
                'ru-RU' : 'Запустить',
                'zh-CN' : '--'},

    'QBackendPanel.stop':{
                'en-US' : 'Stop',
                'ru-RU' : 'Остановить',
                'zh-CN' : '--'},

    'QBackendPanel.reset_settings':{
                'en-US' : 'Reset settings',
                'ru-RU' : 'Сбросить настройки',
                'zh-CN' : '--'},

    'QBackendPanel.FPS':{
                'en-US' : 'FPS',
                'ru-RU' : 'к/с',
                'zh-CN' : '--'},

    'QDFLAppWindow.file':{
                'en-US' : 'File',
                'ru-RU' : 'Файл',
                'zh-CN' : '--'},

    'QDFLAppWindow.language':{
                'en-US' : 'Language',
                'ru-RU' : 'Язык',
                'zh-CN' : '--'},

    'QDFLAppWindow.reset_modules_settings':{
                'en-US' : 'Reset modules settings',
                'ru-RU' : 'Сбросить настройки модулей',
                'zh-CN' : '--'},


    'QDFLAppWindow.reinitialize':{
                'en-US' : 'Reinitialize',
                'ru-RU' : 'Переинициализировать',
                'zh-CN' : '--'},

    'QDFLAppWindow.quit':{
                'en-US' : 'Quit',
                'ru-RU' : 'Выход',
                'zh-CN' : '--'},

    'QDFLAppWindow.help':{
                'en-US' : 'Help',
                'ru-RU' : 'Помощь',
                'zh-CN' : '--'},

    'QDFLAppWindow.visit_github_page':{
                'en-US' : 'Visit github page',
                'ru-RU' : 'Посетить github страницу',
                'zh-CN' : '--'},

    'QDFLAppWindow.process_priority':{
                'en-US' : 'Process priority',
                'ru-RU' : 'Приоритет процесса',
                'zh-CN' : '--'},

    'QDFLAppWindow.process_priority.lowest':{
                'en-US' : 'Lowest',
                'ru-RU' : 'Наименьший',
                'zh-CN' : '--'},

    'QDFLAppWindow.process_priority.normal':{
                'en-US' : 'Normal',
                'ru-RU' : 'Нормальный',
                'zh-CN' : '--'},

    'QFileSource.module_title':{
                'en-US' : 'File source',
                'ru-RU' : 'Файловый источник',
                'zh-CN' : '--'},

    'QFileSource.target_width':{
                'en-US' : 'Target width',
                'ru-RU' : 'Целевая ширина',
                'zh-CN' : '--'},

    'QFileSource.help.target_width':{
                'en-US' : 'Resize the frame to the desired width.',
                'ru-RU' : 'Изменение размера изображения в желаемое.',
                'zh-CN' : '--'},

    'QFileSource.fps':{
                'en-US' : 'FPS',
                'ru-RU' : 'Кадр/сек',
                'zh-CN' : '--'},

    'QFileSource.help.fps':{
                'en-US' : 'Set desired frames per second.',
                'ru-RU' : 'Установите желаемое кадр/сек.',
                'zh-CN' : '--'},

    'QFileSource.is_realtime':{
                'en-US' : 'Real time',
                'ru-RU' : 'Реальное время',
                'zh-CN' : '--'},

    'QFileSource.help.is_realtime':{
                'en-US' : 'Whether to play in real-time FPS or as fast as possible.',
                'ru-RU' : 'Проигрывать в реальном времени или как можно быстрее.',
                'zh-CN' : '--'},


    'QFileSource.is_autorewind':{
                'en-US' : 'Auto rewind',
                'ru-RU' : 'Авто перемотка',
                'zh-CN' : '--'},

    'QCameraSource.module_title':{
                'en-US' : 'Camera source',
                'ru-RU' : 'Источник камеры',
                'zh-CN' : '--'},

    'QCameraSource.device_index':{
                'en-US' : 'Device index',
                'ru-RU' : 'Индекс устройства',
                'zh-CN' : '--'},

    'QCameraSource.driver':{
                'en-US' : 'Driver',
                'ru-RU' : 'Драйвер',
                'zh-CN' : '--'},

    'QCameraSource.help.driver':{
                'en-US' : "OS driver to operate the camera.\nSome drivers can support higher resolution, but don't support vendor's settings.",
                'ru-RU' : "Драйвер ОС для оперирования камерой.\nНекоторые драйверы могут поддерживать выше разрешение, но не поддерживают настройки производителя.",
                'zh-CN' : '--'},

    'QCameraSource.resolution':{
                'en-US' : 'Resolution',
                'ru-RU' : 'Разрешение',
                'zh-CN' : '--'},

    'QCameraSource.help.resolution':{
                'en-US' : 'Output resolution of the camera device.',
                'ru-RU' : 'Выходное разрешение устройства камеры.',
                'zh-CN' : '--'},

    'QCameraSource.fps':{
                'en-US' : 'FPS',
                'ru-RU' : 'Кадр/сек',
                'zh-CN' : '--'},

    'QCameraSource.help.fps':{
                'en-US' : 'Output frame per second of the camera device.',
                'ru-RU' : 'Выходное кадр/сек устройства камеры.',
                'zh-CN' : '--'},

    'QCameraSource.rotation':{
                'en-US' : 'Rotation',
                'ru-RU' : 'Поворот',
                'zh-CN' : '--'},

    'QCameraSource.flip_horizontal':{
                'en-US' : 'Flip horizontal',
                'ru-RU' : 'Отразить гориз.',
                'zh-CN' : '--'},

    'QCameraSource.camera_settings':{
                'en-US' : 'Camera settings',
                'ru-RU' : 'Настройки камеры',
                'zh-CN' : '--'},

    'QCameraSource.open_settings':{
                'en-US' : 'Open',
                'ru-RU' : 'Откр',
                'zh-CN' : '--'},

    'QCameraSource.load_settings':{
                'en-US' : 'Load',
                'ru-RU' : 'Загр',
                'zh-CN' : '--'},

    'QCameraSource.save_settings':{
                'en-US' : 'Save',
                'ru-RU' : 'Сохр',
                'zh-CN' : '--'},

    'QFaceDetector.module_title':{
                'en-US' : 'Face detector',
                'ru-RU' : 'Детектор лиц',
                'zh-CN' : '--'},

    'QFaceDetector.detector_type':{
                'en-US' : 'Detector',
                'ru-RU' : 'Детектор',
                'zh-CN' : '--'},

    'QFaceDetector.help.detector_type':{
                'en-US' : 'Different types of detectors work differently.',
                'ru-RU' : 'Разные типы детекторов работают по-разному.',
                'zh-CN' : '--'},

    'QFaceDetector.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '--'},

    'QFaceDetector.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '--'},

    'QFaceDetector.window_size':{
                'en-US' : 'Window size',
                'ru-RU' : 'Размер окна',
                'zh-CN' : '--'},

    'QFaceDetector.help.window_size':{
                'en-US' : 'Less window size is faster, but less accurate.',
                'ru-RU' : 'Меньший размер окна быстрее, но менее точен.',
                'zh-CN' : '--'},

    'QFaceDetector.threshold':{
                'en-US' : 'Threshold',
                'ru-RU' : 'Порог',
                'zh-CN' : '--'},

    'QFaceDetector.help.threshold':{
                'en-US' : 'The lower value the more false faces will be detected.',
                'ru-RU' : 'Меньшее значение генерирует больше ложноположительных лиц.',
                'zh-CN' : '--'},

    'QFaceDetector.max_faces':{
                'en-US' : 'Max faces',
                'ru-RU' : 'Макс лиц',
                'zh-CN' : '--'},

    'QFaceDetector.help.max_faces':{
                'en-US' : 'Max amount of faces to be detected.',
                'ru-RU' : 'Максимальное кол-во лиц, которое может быть определено.',
                'zh-CN' : '--'},

    'QFaceDetector.sort_by':{
                'en-US' : 'Sort by',
                'ru-RU' : 'Сорт по',
                'zh-CN' : '--'},

    'QFaceDetector.help.sort_by':{
                'en-US' : 'Sort faces by method.',
                'ru-RU' : 'Сортировать лица по выбранному методу.',
                'zh-CN' : '--'},

    'QFaceDetector.temporal_smoothing':{
                'en-US' : 'Temporal smoothing',
                'ru-RU' : 'Сглаживание по времени',
                'zh-CN' : '--'},

    'QFaceDetector.help.temporal_smoothing':{
                'en-US' : 'Stabilizes face rectangle by averaging over the frames.\nGood for use in static scenes or with a webcam.',
                'ru-RU' : 'Стабилизирует прямугольник лица усреднением по кадрам.\nХорошо для использования в статичных сценах или с вебкамерой.',
                'zh-CN' : '--'},

    'QFaceDetector.detected_faces':{
                'en-US' : 'Detected faces',
                'ru-RU' : 'Обнаруженные лица',
                'zh-CN' : '--'},

    'QFaceAligner.module_title':{
                'en-US' : 'Face aligner',
                'ru-RU' : 'Выравниватель лица',
                'zh-CN' : '--'},

    'QFaceAligner.face_coverage':{
                'en-US' : 'Face coverage',
                'ru-RU' : 'Покрытие лица',
                'zh-CN' : '--'},

    'QFaceAligner.help.face_coverage':{
                'en-US' : 'Output area of aligned face.\nAdjust it as you wish.',
                'ru-RU' : 'Площадь выровненного лица. Настройте по своему усмотрению.',
                'zh-CN' : '--'},

    'QFaceAligner.resolution':{
                'en-US' : 'Resolution',
                'ru-RU' : 'Разрешение',
                'zh-CN' : '--'},

    'QFaceAligner.help.resolution':{
                'en-US' : 'Resolution of aligned face.\nShould match model resolution.',
                'ru-RU' : 'Разрешение выровненного лица. Должно совпадать с разрешением модели.',
                'zh-CN' : '--'},

    'QFaceAligner.exclude_moving_parts':{
                'en-US' : 'Exclude moving parts',
                'ru-RU' : 'Исключить движ части',
                'zh-CN' : '--'},

    'QFaceAligner.help.exclude_moving_parts':{
                'en-US' : 'Increase stabilization by excluding landmarks of moving parts of the face, such as mouth and other.',
                'ru-RU' : 'Улучшить стабилизацию исключением лицевых точек\nдвижущихся частей лица, таких как рот и других.',
                'zh-CN' : '--'},

    'QFaceMarker.module_title':{
                'en-US' : 'Face marker',
                'ru-RU' : 'Маркер лица',
                'zh-CN' : '--'},

    'QFaceMarker.marker_type':{
                'en-US' : 'Marker',
                'ru-RU' : 'Маркер',
                'zh-CN' : '--'},

    'QFaceMarker.help.marker_type':{
                'en-US' : 'Type of face marker.',
                'ru-RU' : 'Тип лицевого маркера.',
                'zh-CN' : '--'},

    'QFaceMarker.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '--'},

    'QFaceMarker.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '--'},

    'QFaceMarker.marker_coverage':{
                'en-US' : 'Marker coverage',
                'ru-RU' : 'Покрытие маркера',
                'zh-CN' : '--'},

    'QFaceMarker.help.marker_coverage':{
                'en-US' : 'Controls rectangle size of the detected face to feed into the FaceMarker.\nAdjust it as you wish.',
                'ru-RU' : 'Размер прямоугольника детектированного лица при поступлении в маркер лица.\nНастройте по своему усмотрению.',
                'zh-CN' : '--'},

    'QFaceMarker.temporal_smoothing':{
                'en-US' : 'Temporal smoothing',
                'ru-RU' : 'Сглаживание по времени',
                'zh-CN' : '--'},

    'QFaceMarker.help.temporal_smoothing':{
                'en-US' : 'Stabilizes face landmarks by averaging over the frames.\nGood for use in static scenes or with a webcam.',
                'ru-RU' : 'Стабилизирует лицевые точки усреднением по кадрам.\nХорошо для использования в статичных сценах или с вебкамерой.',
                'zh-CN' : '--'},

    'QFaceSwapper.module_title':{
                'en-US' : 'Face swapper',
                'ru-RU' : 'Замена лица',
                'zh-CN' : '--'},

    'QFaceSwapper.model':{
                'en-US' : 'Model',
                'ru-RU' : 'Модель',
                'zh-CN' : '--'},

    'QFaceSwapper.help.model':{
                'en-US' : 'Model file from a folder or available for download from the Internet.\nYou can train your own model in DeepFaceLab.',
                'ru-RU' : 'Файл модели из папки, либо доступные для загрузки из интернета.\nВы можете натренировать свою собственную модель в прогармме DeepFaceLab.',
                'zh-CN' : '--'},

    'QFaceSwapper.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '--'},

    'QFaceSwapper.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '--'},

    'QFaceSwapper.face_id':{
                'en-US' : 'Face ID',
                'ru-RU' : 'Номер лица',
                'zh-CN' : '--'},

    'QFaceSwapper.help.face_id':{
                'en-US' : 'Face ID to swap.',
                'ru-RU' : 'Номер лица для замены',
                'zh-CN' : '--'},

    'QFaceSwapper.morph_factor':{
                'en-US' : 'Morph factor',
                'ru-RU' : 'Степень морфа',
                'zh-CN' : '--'},

    'QFaceSwapper.help.morph_factor':{
                'en-US' : 'Controls degree of face morph from source to celeb.',
                'ru-RU' : 'Контролирует степень морфа лица от исходного в знаменитость.',
                'zh-CN' : '--'},

    'QFaceSwapper.presharpen_amount':{
                'en-US' : 'Pre-sharpen',
                'ru-RU' : 'Пред-резкость',
                'zh-CN' : '--'},

    'QFaceSwapper.help.presharpen_amount':{
                'en-US' : 'Sharpen the image before feed into the neural network.',
                'ru-RU' : 'Увеличить резкость лица до замены в нейронной сети.',
                'zh-CN' : '--'},

    'QFaceSwapper.pregamma':{
                'en-US' : 'Pre-gamma',
                'ru-RU' : 'Пред-гамма',
                'zh-CN' : '--'},

    'QFaceSwapper.help.pregamma':{
                'en-US' : 'Change gamma of the image before feed into the neural network.',
                'ru-RU' : 'Изменить гамму лица до замены в нейронной сети.',
                'zh-CN' : '--'},

    'QFaceSwapper.two_pass':{
                'en-US' : 'Two pass',
                'ru-RU' : '2 прохода',
                'zh-CN' : '--'},

    'QFaceSwapper.help.two_pass':{
                'en-US' : 'Process the face twice. Reduces the fps by a factor of 2.',
                'ru-RU' : 'Обработать лицо дважды. Снижает кадр/сек в 2 раза.',
                'zh-CN' : '--'},

    'QFrameAdjuster.module_title':{
                'en-US' : 'Frame adjuster',
                'ru-RU' : 'Корректировка кадра',
                'zh-CN' : '--'},

    'QFrameAdjuster.median_blur_per':{
                'en-US' : 'Median blur',
                'ru-RU' : 'Медиан разм',
                'zh-CN' : '--'},

    'QFrameAdjuster.help.median_blur_per':{
                'en-US' : 'Blur whole frame using median filter.',
                'ru-RU' : 'Размыть весь кадр, используя медианный фильтр.',
                'zh-CN' : '--'},

    'QFrameAdjuster.degrade_bicubic_per':{
                'en-US' : 'Degrade bicubic',
                'ru-RU' : 'Бикубик деград',
                'zh-CN' : '--'},

    'QFrameAdjuster.help.degrade_bicubic_per':{
                'en-US' : 'Degrade whole frame using bicubic resize.',
                'ru-RU' : 'Ухудшить весь кадр, используя бикубическое изменение размера.',
                'zh-CN' : '--'},

    'QFaceMerger.module_title':{
                'en-US' : 'Face merger',
                'ru-RU' : 'Склейка лица',
                'zh-CN' : '--'},

    'QFaceMerger.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '--'},

    'QFaceMerger.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '--'},

    'QFaceMerger.face_x_offset':{
                'en-US' : 'Face X offset',
                'ru-RU' : 'Смещение лица X',
                'zh-CN' : '--'},

    'QFaceMerger.face_y_offset':{
                'en-US' : 'Face Y offset',
                'ru-RU' : 'Смещение лица Y',
                'zh-CN' : '--'},

    'QFaceMerger.face_scale':{
                'en-US' : 'Face scale',
                'ru-RU' : 'Масштаб лица',
                'zh-CN' : '--'},

    'QFaceMerger.face_mask_type':{
                'en-US' : 'Face mask type',
                'ru-RU' : 'Тип маски лица',
                'zh-CN' : '--'},

    'QFaceMerger.face_mask_erode':{
                'en-US' : 'Face mask erode',
                'ru-RU' : 'Укорочение маски',
                'zh-CN' : '--'},

    'QFaceMerger.face_mask_blur':{
                'en-US' : 'Face mask blur',
                'ru-RU' : 'Размытие маски',
                'zh-CN' : '--'},

    'QFaceMerger.face_opacity':{
                'en-US' : 'Face opacity',
                'ru-RU' : 'Непрозрач. лица',
                'zh-CN' : '--'},

    'QStreamOutput.module_title':{
                'en-US' : 'Stream output',
                'ru-RU' : 'Выходной поток',
                'zh-CN' : '--'},

    'QStreamOutput.avg_fps':{
                'en-US' : 'Average FPS',
                'ru-RU' : 'Среднее кадр/сек',
                'zh-CN' : '--'},

    'QStreamOutput.help.avg_fps':{
                'en-US' : 'Average FPS of output stream.',
                'ru-RU' : 'Среднее кадр/сек выходного стрима.',
                'zh-CN' : '--'},

    'QStreamOutput.source_type':{
                'en-US' : 'Source',
                'ru-RU' : 'Источник',
                'zh-CN' : '--'},

    'QStreamOutput.show_hide_window':{
                'en-US' : 'window',
                'ru-RU' : 'окно',
                'zh-CN' : '--'},

    'QStreamOutput.aligned_face_id':{
                'en-US' : 'Face ID',
                'ru-RU' : 'Номер лица',
                'zh-CN' : '--'},

    'QStreamOutput.help.aligned_face_id':{
                'en-US' : 'ID of aligned face to show.',
                'ru-RU' : 'Номер выровненного лица для показа.',
                'zh-CN' : '--'},

    'QStreamOutput.target_delay':{
                'en-US' : 'Target delay',
                'ru-RU' : 'Целев. задержка',
                'zh-CN' : '--'},

    'QStreamOutput.help.target_delay':{
                'en-US' : 'Target delay in milliseconds between input frame and output frame.\nMatch this value with audio delay in your stream software to get syncronized stream.',
                'ru-RU' : 'Целевая задержка в миллисекундах между входным и выходным кадрами.\nСовместите это значение с аудио задержкой в вашем стриминговом софте для получения синхронизированного потока.',
                'zh-CN' : '--'},

    'QStreamOutput.save_sequence_path':{
                'en-US' : 'Save sequence',
                'ru-RU' : 'Сохр. секвенцию',
                'zh-CN' : '--'},

    'QStreamOutput.help.save_sequence_path':{
                'en-US' : 'Save image sequence of output stream to the directory.',
                'ru-RU' : 'Сохранить выходной стрим в виде набора изображений в директорию.',
                'zh-CN' : '--'},

    'QStreamOutput.save_sequence_path':{
                'en-US' : 'Save sequence',
                'ru-RU' : 'Сохр. секвенцию',
                'zh-CN' : '--'},

    'QStreamOutput.help.save_sequence_path':{
                'en-US' : 'Save image sequence of output stream to the directory.',
                'ru-RU' : 'Сохранить выходной стрим в виде набора изображений в директорию.',
                'zh-CN' : '--'},

    'QStreamOutput.save_fill_frame_gap':{
                'en-US' : 'Fill frame gap',
                'ru-RU' : 'Заполнить пустоты',
                'zh-CN' : '--'},

    'QStreamOutput.help.save_fill_frame_gap':{
                'en-US' : 'Fill frame drops by duplicating last frame.',
                'ru-RU' : 'Заполнить кадровые пустоты дубликатами последнего кадра.',
                'zh-CN' : '--'},

    'QBCFrameViewer.title':{
                'en-US' : 'Source frame',
                'ru-RU' : 'Исходный кадр',
                'zh-CN' : '--'},

    'QBCFaceAlignViewer.title':{
                'en-US' : 'Aligned face',
                'ru-RU' : 'Выровненное лицо',
                'zh-CN' : '--'},

    'QBCFaceSwapViewer.title':{
                'en-US' : 'Swapped face',
                'ru-RU' : 'Заменённое лицо',
                'zh-CN' : '--'},

    'QBCFinalFrameViewer.title':{
                'en-US' : 'Final frame',
                'ru-RU' : 'Финальный кадр',
                'zh-CN' : '--'},

    'FileSource.image_folder':{
                'en-US' : 'Image folder',
                'ru-RU' : 'Папка изображений',
                'zh-CN' : '--'},

    'FileSource.video_file':{
                'en-US' : 'Video file',
                'ru-RU' : 'Видео файл',
                'zh-CN' : '--'},

    'FaceDetector.largest':{
                'en-US' : 'Largest',
                'ru-RU' : 'Наибольшему',
                'zh-CN' : '--'},

    'FaceDetector.dist_from_center':{
                'en-US' : 'Dist from center',
                'ru-RU' : 'Расстоянию от центра',
                'zh-CN' : '--'},

    'FaceSwapper.model_information':{
                'en-US' : 'Model information',
                'ru-RU' : 'Информация о модели',
                'zh-CN' : '--'},

    'FaceSwapper.filename':{
                'en-US' : 'Filename:',
                'ru-RU' : 'Имя файла:',
                'zh-CN' : '--'},

    'FaceSwapper.resolution':{
                'en-US' : 'Resolution:',
                'ru-RU' : 'Разрешение:',
                'zh-CN' : '--'},

    'FaceSwapper.downloading_model':{
                'en-US' : 'Downloading model...',
                'ru-RU' : 'Загрузка модели...',
                'zh-CN' : '--'},

    'FaceMerger.FaceMaskType.SRC':{
                'en-US' : 'Source',
                'ru-RU' : 'Исходный',
                'zh-CN' : '--'},

    'FaceMerger.FaceMaskType.CELEB':{
                'en-US' : 'Celeb',
                'ru-RU' : 'Знаменитость',
                'zh-CN' : '--'},

    'FaceMerger.FaceMaskType.SRC_M_CELEB':{
                'en-US' : 'Source*Celeb',
                'ru-RU' : 'Исходный*Знаменитость',
                'zh-CN' : '--'},

    'StreamOutput.SourceType.ALIGNED_FACE':{
                'en-US' : 'Aligned face',
                'ru-RU' : 'Выровненное лицо',
                'zh-CN' : '--'},
    'StreamOutput.SourceType.SWAPPED_FACE':{
                'en-US' : 'Swapped face',
                'ru-RU' : 'Заменённое лицо',
                'zh-CN' : '--'},
    'StreamOutput.SourceType.MERGED_FRAME':{
                'en-US' : 'Merged frame',
                'ru-RU' : 'Склеенный кадр',
                'zh-CN' : '--'},

    }