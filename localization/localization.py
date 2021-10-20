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
                'zh-CN' : '自动'},

    'misc.menu_select':{
                'en-US' : '--select--',
                'ru-RU' : '--выбрать--',
                'zh-CN' : '选择'},

    'QBackendPanel.start':{
                'en-US' : 'Start',
                'ru-RU' : 'Запустить',
                'zh-CN' : '开始'},

    'QBackendPanel.stop':{
                'en-US' : 'Stop',
                'ru-RU' : 'Остановить',
                'zh-CN' : '停止'},

    'QBackendPanel.reset_settings':{
                'en-US' : 'Reset settings',
                'ru-RU' : 'Сбросить настройки',
                'zh-CN' : '重置设置'},

    'QBackendPanel.FPS':{
                'en-US' : 'FPS',
                'ru-RU' : 'к/с',
                'zh-CN' : '帧率'},

    'QDFLAppWindow.file':{
                'en-US' : 'File',
                'ru-RU' : 'Файл',
                'zh-CN' : '文件'},

    'QDFLAppWindow.language':{
                'en-US' : 'Language',
                'ru-RU' : 'Язык',
                'zh-CN' : '语言'},

    'QDFLAppWindow.reset_modules_settings':{
                'en-US' : 'Reset modules settings',
                'ru-RU' : 'Сбросить настройки модулей',
                'zh-CN' : '重置模块设置'},


    'QDFLAppWindow.reinitialize':{
                'en-US' : 'Reinitialize',
                'ru-RU' : 'Переинициализировать',
                'zh-CN' : '重新初始化'},

    'QDFLAppWindow.quit':{
                'en-US' : 'Quit',
                'ru-RU' : 'Выход',
                'zh-CN' : '退出'},

    'QDFLAppWindow.help':{
                'en-US' : 'Help',
                'ru-RU' : 'Помощь',
                'zh-CN' : '帮助'},

    'QDFLAppWindow.visit_github_page':{
                'en-US' : 'Visit github page',
                'ru-RU' : 'Посетить github страницу',
                'zh-CN' : '访问github官方主页'},

    'QDFLAppWindow.process_priority':{
                'en-US' : 'Process priority',
                'ru-RU' : 'Приоритет процесса',
                'zh-CN' : '处理优先级'},

    'QDFLAppWindow.process_priority.lowest':{
                'en-US' : 'Lowest',
                'ru-RU' : 'Наименьший',
                'zh-CN' : '最低'},

    'QDFLAppWindow.process_priority.normal':{
                'en-US' : 'Normal',
                'ru-RU' : 'Нормальный',
                'zh-CN' : '普通'},

    'QFileSource.module_title':{
                'en-US' : 'File source',
                'ru-RU' : 'Файловый источник',
                'zh-CN' : '文件源'},

    'QFileSource.target_width':{
                'en-US' : 'Target width',
                'ru-RU' : 'Целевая ширина',
                'zh-CN' : '目标宽度'},

    'QFileSource.help.target_width':{
                'en-US' : 'Resize the frame to the desired width.',
                'ru-RU' : 'Изменение размера изображения в желаемое.',
                'zh-CN' : '将画面调整至所需宽度'},

    'QFileSource.fps':{
                'en-US' : 'FPS',
                'ru-RU' : 'Кадр/сек',
                'zh-CN' : '帧率'},

    'QFileSource.help.fps':{
                'en-US' : 'Set desired frames per second.',
                'ru-RU' : 'Установите желаемое кадр/сек.',
                'zh-CN' : '设置每秒所需帧数'},

    'QFileSource.is_realtime':{
                'en-US' : 'Real time',
                'ru-RU' : 'Реальное время',
                'zh-CN' : '实时'},

    'QFileSource.help.is_realtime':{
                'en-US' : 'Whether to play in real-time FPS or as fast as possible.',
                'ru-RU' : 'Проигрывать в реальном времени или как можно быстрее.',
                'zh-CN' : '以实时FPS播放还是以尽可能快的速度播放'},


    'QFileSource.is_autorewind':{
                'en-US' : 'Auto rewind',
                'ru-RU' : 'Авто перемотка',
                'zh-CN' : '循环播放'},

    'QCameraSource.module_title':{
                'en-US' : 'Camera source',
                'ru-RU' : 'Источник камеры',
                'zh-CN' : '摄像机源'},

    'QCameraSource.device_index':{
                'en-US' : 'Device index',
                'ru-RU' : 'Индекс устройства',
                'zh-CN' : '设备序号'},

    'QCameraSource.driver':{
                'en-US' : 'Driver',
                'ru-RU' : 'Драйвер',
                'zh-CN' : '驱动'},

    'QCameraSource.help.driver':{
                'en-US' : "OS driver to operate the camera.\nSome drivers can support higher resolution, but don't support vendor's settings.",
                'ru-RU' : "Драйвер ОС для оперирования камерой.\nНекоторые драйверы могут поддерживать выше разрешение, но не поддерживают настройки производителя.",
                'zh-CN' : '用于操作相机的系统驱动程序。\n某些驱动程序可以支持更高的分辨率，但不支持供应商的设置'},

    'QCameraSource.resolution':{
                'en-US' : 'Resolution',
                'ru-RU' : 'Разрешение',
                'zh-CN' : '分辨率'},

    'QCameraSource.help.resolution':{
                'en-US' : 'Output resolution of the camera device.',
                'ru-RU' : 'Выходное разрешение устройства камеры.',
                'zh-CN' : '相机输出分辨率'},

    'QCameraSource.fps':{
                'en-US' : 'FPS',
                'ru-RU' : 'Кадр/сек',
                'zh-CN' : '帧率'},

    'QCameraSource.help.fps':{
                'en-US' : 'Output frame per second of the camera device.',
                'ru-RU' : 'Выходное кадр/сек устройства камеры.',
                'zh-CN' : '相机输出帧率'},

    'QCameraSource.rotation':{
                'en-US' : 'Rotation',
                'ru-RU' : 'Поворот',
                'zh-CN' : '旋转'},

    'QCameraSource.flip_horizontal':{
                'en-US' : 'Flip horizontal',
                'ru-RU' : 'Отразить гориз.',
                'zh-CN' : '水平翻转'},

    'QCameraSource.camera_settings':{
                'en-US' : 'Camera settings',
                'ru-RU' : 'Настройки камеры',
                'zh-CN' : '相机设置'},

    'QCameraSource.open_settings':{
                'en-US' : 'Open',
                'ru-RU' : 'Откр',
                'zh-CN' : '打开'},

    'QCameraSource.load_settings':{
                'en-US' : 'Load',
                'ru-RU' : 'Загр',
                'zh-CN' : '载入'},

    'QCameraSource.save_settings':{
                'en-US' : 'Save',
                'ru-RU' : 'Сохр',
                'zh-CN' : '保存'},

    'QFaceDetector.module_title':{
                'en-US' : 'Face detector',
                'ru-RU' : 'Детектор лиц',
                'zh-CN' : '人脸检测器'},

    'QFaceDetector.detector_type':{
                'en-US' : 'Detector',
                'ru-RU' : 'Детектор',
                'zh-CN' : '检测器'},

    'QFaceDetector.help.detector_type':{
                'en-US' : 'Different types of detectors work differently.',
                'ru-RU' : 'Разные типы детекторов работают по-разному.',
                'zh-CN' : '不同检测器效果不同'},

    'QFaceDetector.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备'},

    'QFaceDetector.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率'},

    'QFaceDetector.window_size':{
                'en-US' : 'Window size',
                'ru-RU' : 'Размер окна',
                'zh-CN' : '检测窗口大小'},

    'QFaceDetector.help.window_size':{
                'en-US' : 'Less window size is faster, but less accurate.',
                'ru-RU' : 'Меньший размер окна быстрее, но менее точен.',
                'zh-CN' : '检测窗口越小越快，但越不精准'},

    'QFaceDetector.threshold':{
                'en-US' : 'Threshold',
                'ru-RU' : 'Порог',
                'zh-CN' : '检测置信阈值'},

    'QFaceDetector.help.threshold':{
                'en-US' : 'The lower value the more false faces will be detected.',
                'ru-RU' : 'Меньшее значение генерирует больше ложноположительных лиц.',
                'zh-CN' : '阈值越小检测到错误人脸概率越大'},

    'QFaceDetector.max_faces':{
                'en-US' : 'Max faces',
                'ru-RU' : 'Макс лиц',
                'zh-CN' : '最大人脸数'},

    'QFaceDetector.help.max_faces':{
                'en-US' : 'Max amount of faces to be detected.',
                'ru-RU' : 'Максимальное кол-во лиц, которое может быть определено.',
                'zh-CN' : '最大被检测到的人脸数'},

    'QFaceDetector.sort_by':{
                'en-US' : 'Sort by',
                'ru-RU' : 'Сорт по',
                'zh-CN' : '排序'},

    'QFaceDetector.help.sort_by':{
                'en-US' : 'Sort faces by method.',
                'ru-RU' : 'Сортировать лица по выбранному методу.',
                'zh-CN' : '人脸排序方法'},

    'QFaceDetector.temporal_smoothing':{
                'en-US' : 'Temporal smoothing',
                'ru-RU' : 'Сглаживание по времени',
                'zh-CN' : '在时间维度上平滑'},

    'QFaceDetector.help.temporal_smoothing':{
                'en-US' : 'Stabilizes face rectangle by averaging over the frames.\nGood for use in static scenes or with a webcam.',
                'ru-RU' : 'Стабилизирует прямугольник лица усреднением по кадрам.\nХорошо для использования в статичных сценах или с вебкамерой.',
                'zh-CN' : '通过平均帧来稳定面部矩形。\n适用于静态场景或网络直播'},

    'QFaceDetector.detected_faces':{
                'en-US' : 'Detected faces',
                'ru-RU' : 'Обнаруженные лица',
                'zh-CN' : '检测到的人脸'},

    'QFaceAligner.module_title':{
                'en-US' : 'Face aligner',
                'ru-RU' : 'Выравниватель лица',
                'zh-CN' : '人脸对齐器'},

    'QFaceAligner.face_coverage':{
                'en-US' : 'Face coverage',
                'ru-RU' : 'Покрытие лица',
                'zh-CN' : '人脸覆盖范围'},

    'QFaceAligner.help.face_coverage':{
                'en-US' : 'Output area of aligned face.\nAdjust it as you wish.',
                'ru-RU' : 'Площадь выровненного лица. Настройте по своему усмотрению.',
                'zh-CN' : '输出校正后的人脸。\n爱怎么调节就怎么调节。'},

    'QFaceAligner.resolution':{
                'en-US' : 'Resolution',
                'ru-RU' : 'Разрешение',
                'zh-CN' : '分辨率'},

    'QFaceAligner.help.resolution':{
                'en-US' : 'Resolution of aligned face.\nShould match model resolution.',
                'ru-RU' : 'Разрешение выровненного лица. Должно совпадать с разрешением модели.',
                'zh-CN' : '校正后的人脸分辨率。\n需要匹配模型分辨率'},

    'QFaceAligner.exclude_moving_parts':{
                'en-US' : 'Exclude moving parts',
                'ru-RU' : 'Исключить движ части',
                'zh-CN' : '忽略移动区域的人脸特征点'},

    'QFaceAligner.help.exclude_moving_parts':{
                'en-US' : 'Increase stabilization by excluding landmarks of moving parts of the face, such as mouth and other.',
                'ru-RU' : 'Улучшить стабилизацию исключением лицевых точек\nдвижущихся частей лица, таких как рот и других.',
                'zh-CN' : '通过排除面部移动部分（例如嘴巴和其他你懂的）的特征点来提高稳定性。'},
    
    'QFaceAligner.head_mode':{
                'en-US' : 'Head mode',
                'ru-RU' : 'Режим головы',
                'zh-CN' : 'Head mode(没有翻译)'},

    'QFaceAligner.help.head_mode':{
                'en-US' : 'Head mode. Used with HEAD model.',
                'ru-RU' : 'Режим головы. Используется с HEAD моделью.',
                'zh-CN' : 'Head mode. Used with HEAD model.(没有翻译)'},

    'QFaceAligner.x_offset':{
                'en-US' : 'X offset',
                'ru-RU' : 'Смещение по X',
                'zh-CN' : 'X方向偏移'},

    'QFaceAligner.y_offset':{
                'en-US' : 'Y offset',
                'ru-RU' : 'Смещение по Y',
                'zh-CN' : 'Y方向偏移'},

    'QFaceMarker.module_title':{
                'en-US' : 'Face marker',
                'ru-RU' : 'Маркер лица',
                'zh-CN' : '人脸标记器'},

    'QFaceMarker.marker_type':{
                'en-US' : 'Marker',
                'ru-RU' : 'Маркер',
                'zh-CN' : '人脸特征点'},

    'QFaceMarker.help.marker_type':{
                'en-US' : 'Type of face marker.',
                'ru-RU' : 'Тип лицевого маркера.',
                'zh-CN' : '人脸特征点的类型'},

    'QFaceMarker.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备'},

    'QFaceMarker.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率'},

    'QFaceMarker.marker_coverage':{
                'en-US' : 'Marker coverage',
                'ru-RU' : 'Покрытие маркера',
                'zh-CN' : '特征点覆盖范围'},

    'QFaceMarker.help.marker_coverage':{
                'en-US' : 'Controls rectangle size of the detected face to feed into the FaceMarker.\nAdjust it as you wish.',
                'ru-RU' : 'Размер прямоугольника детектированного лица при поступлении в маркер лица.\nНастройте по своему усмотрению.',
                'zh-CN' : '控制检测到的人脸矩形框大小，以输入人脸特征点识别器。\n按需调整。'},

    'QFaceMarker.temporal_smoothing':{
                'en-US' : 'Temporal smoothing',
                'ru-RU' : 'Сглаживание по времени',
                'zh-CN' : '在时间维度上平滑'},

    'QFaceMarker.help.temporal_smoothing':{
                'en-US' : 'Stabilizes face landmarks by averaging over the frames.\nGood for use in static scenes or with a webcam.',
                'ru-RU' : 'Стабилизирует лицевые точки усреднением по кадрам.\nХорошо для использования в статичных сценах или с вебкамерой.',
                'zh-CN' : '通过对取多帧平均来稳定面部特征点。\n适用于静态场景或网络直播。'},

    'QFaceSwapper.module_title':{
                'en-US' : 'Face swapper',
                'ru-RU' : 'Замена лица',
                'zh-CN' : '人脸交换器'},

    'QFaceSwapper.model':{
                'en-US' : 'Model',
                'ru-RU' : 'Модель',
                'zh-CN' : '模型'},

    'QFaceSwapper.help.model':{
                'en-US' : 'Model file from a folder or available for download from the Internet.\nYou can train your own model in DeepFaceLab.',
                'ru-RU' : 'Файл модели из папки, либо доступные для загрузки из интернета.\nВы можете натренировать свою собственную модель в прогармме DeepFaceLab.',
                'zh-CN' : '从本地文件夹载入，没有的话可从deepfacelab官方中文论坛dfldata.xyz下载模型文件。\您可以用 DeepFaceLab 训练自己的模型。'},

    'QFaceSwapper.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备'},

    'QFaceSwapper.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率'},

    'QFaceSwapper.face_id':{
                'en-US' : 'Face ID',
                'ru-RU' : 'Номер лица',
                'zh-CN' : '人脸ID'},

    'QFaceSwapper.help.face_id':{
                'en-US' : 'Face ID to swap.',
                'ru-RU' : 'Номер лица для замены',
                'zh-CN' : '待换的人脸ID'},

    'QFaceSwapper.morph_factor':{
                'en-US' : 'Morph factor',
                'ru-RU' : 'Степень морфа',
                'zh-CN' : '变形因子'},

    'QFaceSwapper.help.morph_factor':{
                'en-US' : 'Controls degree of face morph from source to celeb.',
                'ru-RU' : 'Контролирует степень морфа лица от исходного в знаменитость.',
                'zh-CN' : '控制从源人脸到目标人脸的面部变形程度。'},

    'QFaceSwapper.presharpen_amount':{
                'en-US' : 'Pre-sharpen',
                'ru-RU' : 'Пред-резкость',
                'zh-CN' : '预先锐化'},

    'QFaceSwapper.help.presharpen_amount':{
                'en-US' : 'Sharpen the image before feed into the neural network.',
                'ru-RU' : 'Увеличить резкость лица до замены в нейронной сети.',
                'zh-CN' : '在送入神经网络前提前对图片锐化'},

    'QFaceSwapper.pregamma':{
                'en-US' : 'Pre-gamma',
                'ru-RU' : 'Пред-гамма',
                'zh-CN' : '预先伽马校正'},

    'QFaceSwapper.help.pregamma':{
                'en-US' : 'Change gamma of the image before feed into the neural network.',
                'ru-RU' : 'Изменить гамму лица до замены в нейронной сети.',
                'zh-CN' : '在送入神经网络前提前对图片伽马校正'},

    'QFaceSwapper.two_pass':{
                'en-US' : 'Two pass',
                'ru-RU' : '2 прохода',
                'zh-CN' : '双重处理人脸'},

    'QFaceSwapper.help.two_pass':{
                'en-US' : 'Process the face twice. Reduces the fps by a factor of 2.',
                'ru-RU' : 'Обработать лицо дважды. Снижает кадр/сек в 2 раза.',
                'zh-CN' : '处理面部两次。 fps随之减半'},

    'QFrameAdjuster.module_title':{
                'en-US' : 'Frame adjuster',
                'ru-RU' : 'Корректировка кадра',
                'zh-CN' : '帧调节器'},

    'QFrameAdjuster.median_blur_per':{
                'en-US' : 'Median blur',
                'ru-RU' : 'Медиан разм',
                'zh-CN' : '中值模糊'},

    'QFrameAdjuster.help.median_blur_per':{
                'en-US' : 'Blur whole frame using median filter.',
                'ru-RU' : 'Размыть весь кадр, используя медианный фильтр.',
                'zh-CN' : '使用中值滤波器模糊整个画面'},

    'QFrameAdjuster.degrade_bicubic_per':{
                'en-US' : 'Degrade bicubic',
                'ru-RU' : 'Бикубик деград',
                'zh-CN' : '双立方降采样'},

    'QFrameAdjuster.help.degrade_bicubic_per':{
                'en-US' : 'Degrade whole frame using bicubic resize.',
                'ru-RU' : 'Ухудшить весь кадр, используя бикубическое изменение размера.',
                'zh-CN' : '缩小整个帧'},

    'QFaceMerger.module_title':{
                'en-US' : 'Face merger',
                'ru-RU' : 'Склейка лица',
                'zh-CN' : '人脸融合器'},

    'QFaceMerger.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备'},

    'QFaceMerger.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率。'},

    'QFaceMerger.face_x_offset':{
                'en-US' : 'Face X offset',
                'ru-RU' : 'Смещение лица X',
                'zh-CN' : '人脸X方向偏移'},

    'QFaceMerger.face_y_offset':{
                'en-US' : 'Face Y offset',
                'ru-RU' : 'Смещение лица Y',
                'zh-CN' : '人脸Y方向偏移'},

    'QFaceMerger.face_scale':{
                'en-US' : 'Face scale',
                'ru-RU' : 'Масштаб лица',
                'zh-CN' : '人脸缩放'},

    'QFaceMerger.face_mask_type':{
                'en-US' : 'Face mask type',
                'ru-RU' : 'Тип маски лица',
                'zh-CN' : '人脸遮罩类型'},

    'QFaceMerger.face_mask_erode':{
                'en-US' : 'Face mask erode',
                'ru-RU' : 'Укорочение маски',
                'zh-CN' : '遮罩向内缩边'},

    'QFaceMerger.face_mask_blur':{
                'en-US' : 'Face mask blur',
                'ru-RU' : 'Размытие маски',
                'zh-CN' : '遮罩边缘羽化'},
                
    'QFaceMerger.color_transfer':{
                'en-US' : 'Color transfer',
                'ru-RU' : 'Перенос цвета',
                'zh-CN' : '彩色转印'},
                
    'QFaceMerger.interpolation':{
                'en-US' : 'Interpolation',
                'ru-RU' : 'Интерполяция',
                'zh-CN' : '插值'},
                
    'QFaceMerger.face_opacity':{
                'en-US' : 'Face opacity',
                'ru-RU' : 'Непрозрач. лица',
                'zh-CN' : '人脸透明度'},

    'QStreamOutput.module_title':{
                'en-US' : 'Stream output',
                'ru-RU' : 'Выходной поток',
                'zh-CN' : '视频流输出'},

    'QStreamOutput.avg_fps':{
                'en-US' : 'Average FPS',
                'ru-RU' : 'Среднее кадр/сек',
                'zh-CN' : '平均帧率'},

    'QStreamOutput.help.avg_fps':{
                'en-US' : 'Average FPS of output stream.',
                'ru-RU' : 'Среднее кадр/сек выходного стрима.',
                'zh-CN' : '输出流的平均帧率'},

    'QStreamOutput.source_type':{
                'en-US' : 'Source',
                'ru-RU' : 'Источник',
                'zh-CN' : '源'},

    'QStreamOutput.show_hide_window':{
                'en-US' : 'window',
                'ru-RU' : 'окно',
                'zh-CN' : '窗口显示'},

    'QStreamOutput.aligned_face_id':{
                'en-US' : 'Face ID',
                'ru-RU' : 'Номер лица',
                'zh-CN' : '人脸ID'},

    'QStreamOutput.help.aligned_face_id':{
                'en-US' : 'ID of aligned face to show.',
                'ru-RU' : 'Номер выровненного лица для показа.',
                'zh-CN' : '要展示的人脸ID'},

    'QStreamOutput.target_delay':{
                'en-US' : 'Target delay',
                'ru-RU' : 'Целев. задержка',
                'zh-CN' : '音画延迟'},

    'QStreamOutput.help.target_delay':{
                'en-US' : 'Target delay in milliseconds between input frame and output frame.\nMatch this value with audio delay in your stream software to get syncronized stream.',
                'ru-RU' : 'Целевая задержка в миллисекундах между входным и выходным кадрами.\nСовместите это значение с аудио задержкой в вашем стриминговом софте для получения синхронизированного потока.',
                'zh-CN' : '输入帧和输出帧之间的目标延迟（以毫秒为单位）。\n将此值与流软件中的音频延迟匹配，实现音画同步的输出流。'},

    'QStreamOutput.save_sequence_path':{
                'en-US' : 'Save sequence',
                'ru-RU' : 'Сохр. секвенцию',
                'zh-CN' : '保存序列帧'},

    'QStreamOutput.help.save_sequence_path':{
                'en-US' : 'Save image sequence of output stream to the directory.',
                'ru-RU' : 'Сохранить выходной стрим в виде набора изображений в директорию.',
                'zh-CN' : '将输出流的图像序列保存到目录中。'},

    'QStreamOutput.save_fill_frame_gap':{
                'en-US' : 'Fill frame gap',
                'ru-RU' : 'Заполнить пустоты',
                'zh-CN' : '补帧'},

    'QStreamOutput.help.save_fill_frame_gap':{
                'en-US' : 'Fill frame drops by duplicating last frame.',
                'ru-RU' : 'Заполнить кадровые пустоты дубликатами последнего кадра.',
                'zh-CN' : '用最后帧来填充帧间隙'},

    'QBCFrameViewer.title':{
                'en-US' : 'Source frame',
                'ru-RU' : 'Исходный кадр',
                'zh-CN' : '源画面'},

    'QBCFaceAlignViewer.title':{
                'en-US' : 'Aligned face',
                'ru-RU' : 'Выровненное лицо',
                'zh-CN' : '对齐校正后的脸'},

    'QBCFaceSwapViewer.title':{
                'en-US' : 'Swapped face',
                'ru-RU' : 'Заменённое лицо',
                'zh-CN' : '换后的脸'},

    'QBCFinalFrameViewer.title':{
                'en-US' : 'Final frame',
                'ru-RU' : 'Финальный кадр',
                'zh-CN' : '结果'},

    'FileSource.image_folder':{
                'en-US' : 'Image folder',
                'ru-RU' : 'Папка изображений',
                'zh-CN' : '图片文件夹'},

    'FileSource.video_file':{
                'en-US' : 'Video file',
                'ru-RU' : 'Видео файл',
                'zh-CN' : '视频文件'},

    'FaceDetector.largest':{
                'en-US' : 'Largest',
                'ru-RU' : 'Наибольшему',
                'zh-CN' : '最大'},

    'FaceDetector.dist_from_center':{
                'en-US' : 'Dist from center',
                'ru-RU' : 'Расстоянию от центра',
                'zh-CN' : '离中心的距离'},

    'FaceSwapper.model_information':{
                'en-US' : 'Model information',
                'ru-RU' : 'Информация о модели',
                'zh-CN' : '模型信息'},

    'FaceSwapper.filename':{
                'en-US' : 'Filename:',
                'ru-RU' : 'Имя файла:',
                'zh-CN' : '文件名'},

    'FaceSwapper.resolution':{
                'en-US' : 'Resolution:',
                'ru-RU' : 'Разрешение:',
                'zh-CN' : '分辨率'},

    'FaceSwapper.downloading_model':{
                'en-US' : 'Downloading model...',
                'ru-RU' : 'Загрузка модели...',
                'zh-CN' : '下载模型中...'},

    'FaceMerger.FaceMaskType.SRC':{
                'en-US' : 'Source',
                'ru-RU' : 'Исходный',
                'zh-CN' : '源脸'},

    'FaceMerger.FaceMaskType.CELEB':{
                'en-US' : 'Celeb',
                'ru-RU' : 'Знаменитость',
                'zh-CN' : '目标脸（名人）'},

    'FaceMerger.FaceMaskType.SRC_M_CELEB':{
                'en-US' : 'Source*Celeb',
                'ru-RU' : 'Исходный*Знаменитость',
                'zh-CN' : '源脸*目标脸'},
                
    'StreamOutput.SourceType.SOURCE_FRAME':{
                'en-US' : 'Source frame',
                'ru-RU' : 'Исходный кадр',
                'zh-CN' : '源帧'},

    'StreamOutput.SourceType.ALIGNED_FACE':{
                'en-US' : 'Aligned face',
                'ru-RU' : 'Выровненное лицо',
                'zh-CN' : '对齐校正后的脸'},

    'StreamOutput.SourceType.SWAPPED_FACE':{
                'en-US' : 'Swapped face',
                'ru-RU' : 'Заменённое лицо',
                'zh-CN' : '换后的脸'},

    'StreamOutput.SourceType.MERGED_FRAME':{
                'en-US' : 'Merged frame',
                'ru-RU' : 'Склеенный кадр',
                'zh-CN' : '合成后的画面'},

    'StreamOutput.SourceType.SOURCE_N_MERGED_FRAME':{
                'en-US' : 'Source and merged frame',
                'ru-RU' : 'Исходный и склеенный кадр',
                'zh-CN' : '源和融合后的帧'},
    
    }
