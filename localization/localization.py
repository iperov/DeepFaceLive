import os
from typing import Union

def L(s : Union[str, None]) -> Union[str, None]:
    return Localization.localize(s)

class Localization:
    lang = os.environ.get('__APP_LANGUAGE', 'en-US')
    allowed_langs = ['en-US', 'ru-RU', 'zh-CN', 'es-ES', 'it-IT']

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
                'zh-CN' : '自动',
                'es-ES' : 'auto',
                'it-IT' : 'auto'},

    'misc.menu_select':{
                'en-US' : '--select--',
                'ru-RU' : '--выбрать--',
                'zh-CN' : '选择',
                'es-ES' : '--seleccionar--',
                'it-IT' : '--selezionare--'},

    'QBackendPanel.start':{
                'en-US' : 'Start',
                'ru-RU' : 'Запустить',
                'zh-CN' : '开始',
                'es-ES' : 'Iniciar',
                'it-IT' : 'Avviare'},

    'QBackendPanel.stop':{
                'en-US' : 'Stop',
                'ru-RU' : 'Остановить',
                'zh-CN' : '停止',
                'es-ES' : 'Detener',
                'it-IT' : 'Fermare'},

    'QBackendPanel.reset_settings':{
                'en-US' : 'Reset settings',
                'ru-RU' : 'Сбросить настройки',
                'zh-CN' : '重置设置',
                'es-ES' : 'Restablecer configuración',
                'it-IT' : 'Ripristina le impostazioni'},

    'QBackendPanel.FPS':{
                'en-US' : 'FPS',
                'ru-RU' : 'к/с',
                'zh-CN' : '帧率',
                'es-ES' : 'FPS',
                'it-IT' : 'FPS'},

    'QDFLAppWindow.file':{
                'en-US' : 'File',
                'ru-RU' : 'Файл',
                'zh-CN' : '文件',
                'es-ES' : 'Archivo',
                'it-IT' : 'File'},

    'QDFLAppWindow.language':{
                'en-US' : 'Language',
                'ru-RU' : 'Язык',
                'zh-CN' : '语言',
                'es-ES' : 'Idioma',
                'it-IT' : 'Lingua'},

    'QDFLAppWindow.reset_modules_settings':{
                'en-US' : 'Reset modules settings',
                'ru-RU' : 'Сбросить настройки модулей',
                'zh-CN' : '重置模块设置',
                'es-ES' : 'Restablecer configuración de módulos',
                'it-IT' : 'Ripristina le impostazioni dei moduli'},


    'QDFLAppWindow.reinitialize':{
                'en-US' : 'Reinitialize',
                'ru-RU' : 'Переинициализировать',
                'zh-CN' : '重新初始化',
                'es-ES' : 'Reinicializar',
                'it-IT' : 'Reinizializza'},

    'QDFLAppWindow.quit':{
                'en-US' : 'Quit',
                'ru-RU' : 'Выход',
                'zh-CN' : '退出',
                'es-ES' : 'Salir',
                'it-IT' : 'Esci'},

    'QDFLAppWindow.help':{
                'en-US' : 'Help',
                'ru-RU' : 'Помощь',
                'zh-CN' : '帮助',
                'es-ES' : 'Ayuda',
                'it-IT' : 'Aiuto'},

    'QDFLAppWindow.visit_github_page':{
                'en-US' : 'Visit github page',
                'ru-RU' : 'Посетить github страницу',
                'zh-CN' : '访问github官方主页',
                'es-ES' : 'Visitar página de GitHub',
                'it-IT' : 'Visita la pagina di GitHub'},

    'QDFLAppWindow.process_priority':{
                'en-US' : 'Process priority',
                'ru-RU' : 'Приоритет процесса',
                'zh-CN' : '处理优先级',
                'es-ES' : 'Prioridad del proceso',
                'it-IT' : 'Priorità del processo'},

    'QDFLAppWindow.process_priority.lowest':{
                'en-US' : 'Lowest',
                'ru-RU' : 'Наименьший',
                'zh-CN' : '最低',
                'es-ES' : 'Mínima',
                'it-IT' : 'Bassa'},

    'QDFLAppWindow.process_priority.normal':{
                'en-US' : 'Normal',
                'ru-RU' : 'Нормальный',
                'zh-CN' : '普通',
                'es-ES' : 'Normal',
                'it-IT' : 'Normale'},

    'QFileSource.module_title':{
                'en-US' : 'File source',
                'ru-RU' : 'Файловый источник',
                'zh-CN' : '文件源',
                'es-ES' : 'Origen desde fichero',
                'it-IT' : 'File sorgente'},

    'QFileSource.target_width':{
                'en-US' : 'Target width',
                'ru-RU' : 'Целевая ширина',
                'zh-CN' : '目标宽度',
                'es-ES' : 'Ancho deseado',
                'it-IT' : 'Larghezza obiettivo'},

    'QFileSource.help.target_width':{
                'en-US' : 'Resize the frame to the desired width.',
                'ru-RU' : 'Изменение размера изображения в желаемое.',
                'zh-CN' : '将画面调整至所需宽度',
                'es-ES' : 'Ajustar el frame al tamaño deseado.',
                'it-IT' : "Ridimensiona il fotogramma alla larghezza desiderata."},

    'QFileSource.fps':{
                'en-US' : 'FPS',
                'ru-RU' : 'Кадр/сек',
                'zh-CN' : '帧率',
                'es-ES' : 'FPS',
                'it-IT' : 'FPS'},

    'QFileSource.help.fps':{
                'en-US' : 'Set desired frames per second.',
                'ru-RU' : 'Установите желаемое кадр/сек.',
                'zh-CN' : '设置每秒所需帧数',
                'es-ES' : 'Establecer los fotogramas por segundo deseados.',
                'it-IT' : 'Imposta i fotogrammi per secondo desiderati.'},

    'QFileSource.is_realtime':{
                'en-US' : 'Real time',
                'ru-RU' : 'Реальное время',
                'zh-CN' : '实时',
                'es-ES' : 'Tiempo real',
                'it-IT' : 'Tempo reale'},

    'QFileSource.help.is_realtime':{
                'en-US' : 'Whether to play in real-time FPS or as fast as possible.',
                'ru-RU' : 'Проигрывать в реальном времени или как можно быстрее.',
                'zh-CN' : '以实时FPS播放还是以尽可能快的速度播放',
                'es-ES' : 'Si se desea reproducir los FPS en tiempo real o lo más rápido posible.',
                'it-IT' : 'Se si desidera riprodurre gli FPS in tempo reale o il più veloce possibile.'},


    'QFileSource.is_autorewind':{
                'en-US' : 'Auto rewind',
                'ru-RU' : 'Авто перемотка',
                'zh-CN' : '循环播放',
                'es-ES' : 'Rebobinar automáticamente',
                'it-IT' : 'Riavvolgimento automatico'},

    'QCameraSource.module_title':{
                'en-US' : 'Camera source',
                'ru-RU' : 'Источник камеры',
                'zh-CN' : '摄像机源',
                'es-ES' : 'Origen de cámara',
                'it-IT' : 'Fonte della telecamera'},

    'QCameraSource.device_index':{
                'en-US' : 'Device index',
                'ru-RU' : 'Индекс устройства',
                'zh-CN' : '设备序号',
                'es-ES' : 'Índice de dispositivo',
                'it-IT' : 'Indice del dispositivo'},

    'QCameraSource.driver':{
                'en-US' : 'Driver',
                'ru-RU' : 'Драйвер',
                'zh-CN' : '驱动',
                'es-ES' : 'Controlador',
                'it-IT' : 'Driver'},

    'QCameraSource.help.driver':{
                'en-US' : "OS driver to operate the camera.\nSome drivers can support higher resolution, but don't support vendor's settings.",
                'ru-RU' : "Драйвер ОС для оперирования камерой.\nНекоторые драйверы могут поддерживать выше разрешение, но не поддерживают настройки производителя.",
                'zh-CN' : '用于操作相机的系统驱动程序。\n某些驱动程序可以支持更高的分辨率，但不支持供应商的设置',
                'es-ES' : 'Controlador del sistema operativo para operar la cámara.\nAlgunos controladores pueden soportar una resolución mayor, pero no soportan la configuración del fabricante.',
                'it-IT' : 'Driver del sistema operativo per far funzionare la videocamera.\nAlcuni driver possono supportare una risoluzione più alta, ma non supportano le impostazioni del fornitore.'},

    'QCameraSource.resolution':{
                'en-US' : 'Resolution',
                'ru-RU' : 'Разрешение',
                'zh-CN' : '分辨率',
                'es-ES' : 'Resolución',
                'it-IT' : 'Risoluzione'},

    'QCameraSource.help.resolution':{
                'en-US' : 'Output resolution of the camera device.',
                'ru-RU' : 'Выходное разрешение устройства камеры.',
                'zh-CN' : '相机输出分辨率',
                'es-ES' : 'Resolución de salida del dispositivo cámara.',
                'it-IT' : 'Risoluzione in uscita della telecamera.'},

    'QCameraSource.fps':{
                'en-US' : 'FPS',
                'ru-RU' : 'Кадр/сек',
                'zh-CN' : '帧率',
                'es-ES' : 'FPS',
                'it-IT' : 'FPS'},

    'QCameraSource.help.fps':{
                'en-US' : 'Output frame per second of the camera device.',
                'ru-RU' : 'Выходное кадр/сек устройства камеры.',
                'zh-CN' : '相机输出帧率',
                'es-ES' : 'FPS de salida del dispositivo cámara.',
                'it-IT' : 'FPS in uscita della telecamera'},

    'QCameraSource.rotation':{
                'en-US' : 'Rotation',
                'ru-RU' : 'Поворот',
                'zh-CN' : '旋转',
                'es-ES' : 'Rotación',
                'it-IT' : 'Rotazione'},

    'QCameraSource.flip_horizontal':{
                'en-US' : 'Flip horizontal',
                'ru-RU' : 'Отразить гориз.',
                'zh-CN' : '水平翻转',
                'es-ES' : 'Voltear horizontalmente',
                'it-IT' : 'Capovolgere orizzontalmente'},

    'QCameraSource.camera_settings':{
                'en-US' : 'Camera settings',
                'ru-RU' : 'Настройки камеры',
                'zh-CN' : '相机设置',
                'es-ES' : 'Ajustes de cámara',
                'it-IT' : 'Impostazioni della telecamera'},

    'QCameraSource.open_settings':{
                'en-US' : 'Open',
                'ru-RU' : 'Откр',
                'zh-CN' : '打开',
                'es-ES' : 'Abrir',
                'it-IT' : 'Apri'},

    'QCameraSource.load_settings':{
                'en-US' : 'Load',
                'ru-RU' : 'Загр',
                'zh-CN' : '载入',
                'es-ES' : 'Cargar',
                'it-IT' : 'Carica'},

    'QCameraSource.save_settings':{
                'en-US' : 'Save',
                'ru-RU' : 'Сохр',
                'zh-CN' : '保存',
                'es-ES' : 'Guardar',
                'it-IT' : 'Salva'},

    'QFaceDetector.module_title':{
                'en-US' : 'Face detector',
                'ru-RU' : 'Детектор лиц',
                'zh-CN' : '人脸检测器',
                'es-ES' : 'Detector de caras',
                'it-IT' : 'Rilevatore di facce'},

    'QFaceDetector.detector_type':{
                'en-US' : 'Detector',
                'ru-RU' : 'Детектор',
                'zh-CN' : '检测器',
                'es-ES' : 'Detector',
                'it-IT' : 'Rilevatore'},

    'QFaceDetector.help.detector_type':{
                'en-US' : 'Different types of detectors work differently.',
                'ru-RU' : 'Разные типы детекторов работают по-разному.',
                'zh-CN' : '不同检测器效果不同',
                'es-ES' : 'Diferentes tipos de detecciones funcionan de manera distinta.',
                'it-IT' : 'Diversi tipi di rilevatori funzionano in maniera diversa'},

    'QFaceDetector.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备',
                'es-ES' : 'Dispositivo',
                'it-IT' : 'Dispositivo'},

    'QFaceDetector.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率',
                'es-ES' : 'Ajuste la combinación de dispositivos del módulo para lograr más FPS o una menor utilización de CPU.',
                'it-IT' : 'Regola la combinazione dei dispositivi del modulo per ottenere fps più alti o un minore utilizzo della CPU.'},

    'QFaceDetector.window_size':{
                'en-US' : 'Window size',
                'ru-RU' : 'Размер окна',
                'zh-CN' : '检测窗口大小',
                'es-ES' : 'Tamaño de ventana',
                'it-IT' : 'Dimensione della finestra'},

    'QFaceDetector.help.window_size':{
                'en-US' : 'Less window size is faster, but less accurate.',
                'ru-RU' : 'Меньший размер окна быстрее, но менее точен.',
                'zh-CN' : '检测窗口越小越快，但越不精准',
                'es-ES' : 'Menor tamaño de ventana es más rápido, pero menos preciso.',
                'it-IT' : 'Una dimensione della finestra minore è più veloce, ma meno accurata.'},   

    'QFaceDetector.threshold':{
                'en-US' : 'Threshold',
                'ru-RU' : 'Порог',
                'zh-CN' : '检测置信阈值',
                'es-ES' : 'Umbral',
                'it-IT' : 'Soglia'},

    'QFaceDetector.help.threshold':{
                'en-US' : 'The lower value the more false faces will be detected.',
                'ru-RU' : 'Меньшее значение генерирует больше ложноположительных лиц.',
                'zh-CN' : '阈值越小检测到错误人脸概率越大',
                'es-ES' : 'Cuanto más bajo sea el valor, más caras falsas se detectarán.',
                'it-IT' : 'Più basso è il valore, più false facce saranno rilevate.'},

    'QFaceDetector.max_faces':{
                'en-US' : 'Max faces',
                'ru-RU' : 'Макс лиц',
                'zh-CN' : '最大人脸数',
                'es-ES' : 'Máx. caras',
                'it-IT' : 'Max. facce'},

    'QFaceDetector.help.max_faces':{
                'en-US' : 'Max amount of faces to be detected.',
                'ru-RU' : 'Максимальное кол-во лиц, которое может быть определено.',
                'zh-CN' : '最大被检测到的人脸数',
                'es-ES' : 'Máx. caras a detectar.',
                'it-IT' : 'Nummero massimo di facce da rilevare.'},

    'QFaceDetector.sort_by':{
                'en-US' : 'Sort by',
                'ru-RU' : 'Сорт по',
                'zh-CN' : '排序',
                'es-ES' : 'Ordenar por',
                'it-IT' : 'Ordina per'},

    'QFaceDetector.help.sort_by':{
                'en-US' : 'Sort faces by method. For example, for "RIGHT TO LEFT" the Face ID 0 will be at the rightmost part of the screen.',
                'ru-RU' : 'Сортировать лица по выбранному методу. Например, для "СПРАВА НАЛЕВО" лица с идентификатором 0 будет находиться в самой правой части экрана.',
                'zh-CN' : '人脸排序方法 例如，对于 "从右到左"，Face ID 0将在屏幕的最右边',
                'es-ES' : 'Ordenar caras por método. Por ejemplo, para "DE DERECHA A IZQUIERDA" la cara con ID 0 estará en la parte más a la derecha de la pantalla.',
                'it-IT' : "Ordina le facce per metodo. Per esempio, per \"DA DESTRA A SINISTRA\" l'ID del volto 0 sarà nella parte più a destra dello schermo."},

    'QFaceDetector.temporal_smoothing':{
                'en-US' : 'Temporal smoothing',
                'ru-RU' : 'Сглаживание по времени',
                'zh-CN' : '在时间维度上平滑',
                'es-ES' : 'Suavizado temporal',
                'it-IT' : 'Smussamento temporale'},

    'QFaceDetector.help.temporal_smoothing':{
                'en-US' : 'Stabilizes face rectangle by averaging over the frames.\nGood for use in static scenes or with a webcam.',
                'ru-RU' : 'Стабилизирует прямугольник лица усреднением по кадрам.\nХорошо для использования в статичных сценах или с вебкамерой.',
                'zh-CN' : '通过平均帧来稳定面部矩形。\n适用于静态场景或网络直播',
                'es-ES' : 'Estabiliza el rectángulo de la cara promediando los fotogramas.\nBueno para usar en escenas estáticas o con cámaras web.',
                'it-IT' : 'Stabilizza il rettangolo del volto facendo la media dei fotogrammi.\nBuono da usare in scene statiche o con una webcam.'},

    'QFaceDetector.detected_faces':{
                'en-US' : 'Detected faces',
                'ru-RU' : 'Обнаруженные лица',
                'zh-CN' : '检测到的人脸',
                'es-ES' : 'Caras detectadas',
                'it-IT' : 'Facce rilevate'},

    'QFaceAligner.module_title':{
                'en-US' : 'Face aligner',
                'ru-RU' : 'Выравниватель лица',
                'zh-CN' : '人脸对齐器',
                'es-ES' : 'Alineador de caras',
                'it-IT' : 'Allineatore facciale'},

    'QFaceAligner.face_coverage':{
                'en-US' : 'Face coverage',
                'ru-RU' : 'Покрытие лица',
                'zh-CN' : '人脸覆盖范围',
                'es-ES' : 'Cobertura facial',
                'it-IT' : 'Copertura facciale'},

    'QFaceAligner.help.face_coverage':{
                'en-US' : 'Output area of aligned face.\nAdjust it as you wish.',
                'ru-RU' : 'Площадь выровненного лица. Настройте по своему усмотрению.',
                'zh-CN' : '输出校正后的人脸。\n爱怎么调节就怎么调节。',
                'es-ES' : 'Área de salida del rostro alineado.\nAjústelo como desee.',
                'it-IT' : 'Area di uscita della faccia allineata.\nRegolatelo come volete.'},

    'QFaceAligner.resolution':{
                'en-US' : 'Resolution',
                'ru-RU' : 'Разрешение',
                'zh-CN' : '分辨率',
                'es-ES' : 'Resolución',
                'it-IT' : 'Risoluzione'},

    'QFaceAligner.help.resolution':{
                'en-US' : 'Resolution of aligned face.\nShould match model resolution.',
                'ru-RU' : 'Разрешение выровненного лица. Должно совпадать с разрешением модели.',
                'zh-CN' : '校正后的人脸分辨率。\n需要匹配模型分辨率',
                'es-ES' : 'Resolución del rostro alineado.\nDebe coincidir con la resolución del modelo.',
                'it-IT' : 'Risoluzione della faccia allineata.\nDovrebbe corrispondere alla risoluzione del modello'},

    'QFaceAligner.exclude_moving_parts':{
                'en-US' : 'Exclude moving parts',
                'ru-RU' : 'Исключить движ части',
                'zh-CN' : '忽略移动区域的人脸特征点',
                'es-ES' : 'Excluir las partes móviles'},
                'it-IT' : 'Escludi parti mobili',

    'QFaceAligner.help.exclude_moving_parts':{
                'en-US' : 'Increase stabilization by excluding landmarks of moving parts of the face, such as mouth and other.',
                'ru-RU' : 'Улучшить стабилизацию исключением лицевых точек\nдвижущихся частей лица, таких как рот и других.',
                'zh-CN' : '通过排除面部移动部分（例如嘴巴和其他你懂的）的特征点来提高稳定性。',
                'es-ES' : 'Aumentar la estabilización excluyendo los puntos de referencia de las partes móviles de la cara, como la boca y otros',
                'it-IT' : 'Aumenta la stabilità escludendo i punti di riferimento delle parti mobili della faccia, come la bocca e altri.'},

    'QFaceAligner.head_mode':{
                'en-US' : 'Head mode',
                'ru-RU' : 'Режим головы',
                'zh-CN' : 'Head mode(没有翻译)',
                'es-ES' : 'Modo HEAD',
                'it-IT' : 'Modalità Testa (HEAD)'},

    'QFaceAligner.help.head_mode':{
                'en-US' : 'Head mode. Used with HEAD model.',
                'ru-RU' : 'Режим головы. Используется с HEAD моделью.',
                'zh-CN' : 'Head mode. Used with HEAD model.(没有翻译)',
                'es-ES' : 'Modo HEAD. Usado con el modelo HEAD.',
                'it-IT' : 'Modalità testa. Usala con un modello HEAD.'},

    'QFaceAligner.x_offset':{
                'en-US' : 'X offset',
                'ru-RU' : 'Смещение по X',
                'zh-CN' : 'X方向偏移',
                'es-ES' : 'Desplazamiento en X'},
                'it-IT' : 'Compensazione X',

    'QFaceAligner.y_offset':{
                'en-US' : 'Y offset',
                'ru-RU' : 'Смещение по Y',
                'zh-CN' : 'Y方向偏移',
                'es-ES' : 'Desplazamiento en Y',
                'it-IT' : 'Compensazione Y'},

    'QFaceMarker.module_title':{
                'en-US' : 'Face marker',
                'ru-RU' : 'Маркер лица',
                'zh-CN' : '人脸标记器',
                'es-ES' : 'Marcador de caras',
                'it-IT' : 'Marcatore facciale'},

    'QFaceMarker.marker_type':{
                'en-US' : 'Marker',
                'ru-RU' : 'Маркер',
                'zh-CN' : '人脸特征点',
                'es-ES' : 'Marcador',
                'it-IT' : 'Marcatore'},

    'QFaceMarker.help.marker_type':{
                'en-US' : 'Type of face marker.',
                'ru-RU' : 'Тип лицевого маркера.',
                'zh-CN' : '人脸特征点的类型',
                'es-ES' : 'Tipo de marcador de caras.',
                'it-IT' : 'Tipo di marcatore facciale.'},

    'QFaceMarker.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备',
                'es-ES' : 'Dispositivo',
                'it-IT' : 'Dispositivo'},

    'QFaceMarker.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率',
                'es-ES' : 'Ajuste la combinación de dispositivos del módulo para alcanzar un mayor número de FPS o una menor carga de CPU.',
                'it-IT' : 'Regola la combinazione dei dispositivi del modulo per ottenere FPS più alti o un utilizzo più basso della CPU'},

    'QFaceMarker.marker_coverage':{
                'en-US' : 'Marker coverage',
                'ru-RU' : 'Покрытие маркера',
                'zh-CN' : '特征点覆盖范围',
                'es-ES' : 'Cobertura del marcador',
                'it-IT' : 'Copertura del marcatore'},

    'QFaceMarker.help.marker_coverage':{
                'en-US' : 'Controls rectangle size of the detected face to feed into the FaceMarker.\nGreen facial points must exactly match the face.\nLook at "Aligned Face" window and adjust it as you wish.',
                'ru-RU' : 'Размер прямоугольника детектированного лица при поступлении в маркер лица.\nЗеленые лицевые точки должны точно соответстовать лицу.\nСмотрите на окно "Выровненное лицо" и настройте по своему усмотрению.',
                'zh-CN' : '控制检测到的人脸矩形框大小，以输入人脸特征点识别器。\n绿色面部点必须与面部完全匹配\n查看 "对齐的面 "窗口，并按你的意愿进行调整。',
                'es-ES' : 'Controla el tamaño del rectángulo de la cara detectada para procesarlo en el marcador de caras (FaceMarker).\nLos puntos faciales verdes deben coincidir exactamente con la cara.\nMire en la ventana "Caras Alineadas" y ajuste según su gusto.',
                'it-IT' : 'Controlla la dimensione del rettangolo della faccia rilevata da inserire nel marcatore facciale (FaceMarker).\nI punti facciali verdi devono corrispondere esattamente al viso.\nGuarda alla finestra "Faccie allineate" per regolare come desideri'},

    'QFaceMarker.temporal_smoothing':{
                'en-US' : 'Temporal smoothing',
                'ru-RU' : 'Сглаживание по времени',
                'zh-CN' : '在时间维度上平滑',
                'es-ES' : 'Suavizado temporal',
                'it-IT' : 'Smussamento temporale'},

    'QFaceMarker.help.temporal_smoothing':{
                'en-US' : 'Stabilizes face landmarks by averaging over the frames.\nGood for use in static scenes or with a webcam.',
                'ru-RU' : 'Стабилизирует лицевые точки усреднением по кадрам.\nХорошо для использования в статичных сценах или с вебкамерой.',
                'zh-CN' : '通过对取多帧平均来稳定面部特征点。\n适用于静态场景或网络直播。',
                'es-ES' : 'Estabiliza los puntos de referencia de la cara haciendo un promedio de los fotogramas.\nBueno para usar en escenas estáticas o con cámaras web.',
                'it-IT' : 'Stabilizza i punti di riferimento della faccia facendo la media dei fotogrammi.\nBuono da usare in scene statiche o con una webcam.'},

    'QFaceSwapper.module_title':{
                'en-US' : 'Face swapper',
                'ru-RU' : 'Замена лица',
                'zh-CN' : '人脸交换器',
                'es-ES' : 'Intercambiador de caras',
                'it-IT' : 'Scambiatore di facce'},

    'QFaceSwapper.model':{
                'en-US' : 'Model',
                'ru-RU' : 'Модель',
                'zh-CN' : '模型',
                'es-ES' : 'Modelo',
                'it-IT' : 'Modello'},

    'QFaceSwapper.help.model':{
                'en-US' : 'Model file from a folder or available for download from the Internet.\nYou can train your own model in DeepFaceLab.',
                'ru-RU' : 'Файл модели из папки, либо доступные для загрузки из интернета.\nВы можете натренировать свою собственную модель в прогармме DeepFaceLab.',
                'zh-CN' : '从本地文件夹载入，没有的话可从deepfacelab官方中文论坛dfldata.xyz下载模型文件。\您可以用 DeepFaceLab 训练自己的模型。',
                'es-ES' : 'Archivo de modelo desde una carpeta o disponible para descargar desde Internet.\nPuede entrenar su propio modelo en DeepFaceLab.',
                'it-IT' : 'File del modello da una cartella or disponibile per il download da internet.\nPuoi addestrare il tuo modello su DeepFaceLab.'},

    'QFaceSwapper.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备',
                'es-ES' : 'Dispositivo',
                'it-IT' : 'Dispositivo'},

    'QFaceSwapper.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率',
                'es-ES' : 'Ajuste la combinación de dispositivos del módulo para alcanzar un mayor número de FPS o una menor carga de CPU.',
                'it-IT' : 'Regola la combinazione dei dispositivi del modulo per ottenere FPS più alti o un utilizzo più basso della CPU'},

    'QFaceSwapper.swap_all_faces':{
                'en-US' : 'Swap all faces',
                'ru-RU' : 'Заменить все лица',
                'zh-CN' : '改变所有面孔',
                'es-ES' : 'Intercambiar todas las caras',
                'it-IT' : 'Scambia tutte le facce'},

    'QFaceSwapper.face_id':{
                'en-US' : 'Face ID',
                'ru-RU' : 'Номер лица',
                'zh-CN' : '人脸ID',
                'es-ES' : 'ID de la cara',
                'it-IT' : 'ID della faccia'},

    'QFaceSwapper.help.face_id':{
                'en-US' : 'Face ID to swap.',
                'ru-RU' : 'Номер лица для замены',
                'zh-CN' : '待换的人脸ID',
                'es-ES' : 'ID de la cara a intercambiar',
                'it-IT' : 'ID della faccia da scambiare.'},

    'QFaceSwapper.morph_factor':{
                'en-US' : 'Morph factor',
                'ru-RU' : 'Степень морфа',
                'zh-CN' : '变形因子',
                'es-ES' : 'Factor de transformación',
                'it-IT' : 'Fattore morfologico'},

    'QFaceSwapper.help.morph_factor':{
                'en-US' : 'Controls degree of face morph from source to celeb.',
                'ru-RU' : 'Контролирует степень морфа лица от исходного в знаменитость.',
                'zh-CN' : '控制从源人脸到目标人脸的面部变形程度。',
                'es-ES' : 'Controla el grado de transformación de la cara desde el origen hasta la celebridad.',
                'it-IT' : 'Controlla il grado del fattore morfologico dalla faccia sorgente alla celebrità'},

    'QFaceSwapper.presharpen_amount':{
                'en-US' : 'Pre-sharpen',
                'ru-RU' : 'Пред-резкость',
                'zh-CN' : '预先锐化',
                'es-ES' : 'Pre-aclarado',
                'it-IT' : 'Pre-nitidezza'},

    'QFaceSwapper.help.presharpen_amount':{
                'en-US' : 'Sharpen the image before feed into the neural network.',
                'ru-RU' : 'Увеличить резкость лица до замены в нейронной сети.',
                'zh-CN' : '在送入神经网络前提前对图片锐化',
                'es-ES' : 'Aclarar la imagen antes de enviarla a la red neuronal.',
                'it-IT' : "Rendere più nitida l'immagine prima di inserirla nella rete neurale."},

    'QFaceSwapper.pregamma':{
                'en-US' : 'Pre-gamma',
                'ru-RU' : 'Пред-гамма',
                'zh-CN' : '预先伽马校正',
                'es-ES' : 'Pre-gamma',
                'it-IT' : 'Pre-gamma'},

    'QFaceSwapper.help.pregamma':{
                'en-US' : 'Change gamma of the image before feed into the neural network.',
                'ru-RU' : 'Изменить гамму лица до замены в нейронной сети.',
                'zh-CN' : '在送入神经网络前提前对图片伽马校正',
                'es-ES' : 'Cambiar el valor gamma de la imagen antes de enviarla a la red neuronal.',
                'it-IT' : "Cambia il gamma dell'immagine prima di inserirla nella rete neurale."},

    'QFaceSwapper.two_pass':{
                'en-US' : 'Two pass',
                'ru-RU' : '2 прохода',
                'zh-CN' : '双重处理人脸',
                'es-ES' : 'Dos pasadas',
                'it-IT' : 'Due passate'},

    'QFaceSwapper.help.two_pass':{
                'en-US' : 'Process the face twice. Reduces the fps by a factor of 2.',
                'ru-RU' : 'Обработать лицо дважды. Снижает кадр/сек в 2 раза.',
                'zh-CN' : '处理面部两次。 fps随之减半',
                'es-ES' : 'Procesar la cara dos veces. Reduce los FPS en un factor de 2.',
                'it-IT' : 'Processa la faccia due volte. Riduce gli FPS di un fattore di 2.'},

    'QFrameAdjuster.module_title':{
                'en-US' : 'Frame adjuster',
                'ru-RU' : 'Корректировка кадра',
                'zh-CN' : '帧调节器',
                'es-ES' : 'Ajustador de cuadro',
                'it-IT' : 'Regolatore del fotogramma'},

    'QFrameAdjuster.median_blur_per':{
                'en-US' : 'Median blur',
                'ru-RU' : 'Медиан разм',
                'zh-CN' : '中值模糊',
                'es-ES' : 'Desenfoque mediana',
                'it-IT' : 'Sfocatura mediana'},

    'QFrameAdjuster.help.median_blur_per':{
                'en-US' : 'Blur whole frame using median filter.',
                'ru-RU' : 'Размыть весь кадр, используя медианный фильтр.',
                'zh-CN' : '使用中值滤波器模糊整个画面',
                'es-ES' : 'Desenfoque de toda la imagen usando el filtro mediana.',
                'it-IT' : "Sfoca l'intero fotogramma usando il filtro mediano."},

    'QFrameAdjuster.degrade_bicubic_per':{
                'en-US' : 'Degrade bicubic',
                'ru-RU' : 'Бикубик деград',
                'zh-CN' : '双立方降采样',
                'es-ES' : 'Degradación bicúbica',
                'it-IT' : 'Degradazione bicubica'},

    'QFrameAdjuster.help.degrade_bicubic_per':{
                'en-US' : 'Degrade whole frame using bicubic resize.',
                'ru-RU' : 'Ухудшить весь кадр, используя бикубическое изменение размера.',
                'zh-CN' : '缩小整个帧',
                'es-ES' : 'Degradar toda la imagen usando el redimensionado bicúbico.',
                'it-IT' : "Degrada l'intero fotogramma usando il ridimensionamento bicubico"},

    'QFaceMerger.module_title':{
                'en-US' : 'Face merger',
                'ru-RU' : 'Склейка лица',
                'zh-CN' : '人脸融合器',
                'es-ES' : 'Fusionador de caras',
                'it-IT' : 'Unitore di facce (Merger)'},

    'QFaceMerger.device':{
                'en-US' : 'Device',
                'ru-RU' : 'Устройство',
                'zh-CN' : '设备',
                'es-ES' : 'Dispositivo',
                'it-IT' : 'Dispositivo'},

    'QFaceMerger.help.device':{
                'en-US' : 'Adjust the combination of module devices to achieve higher fps or lower CPU usage.',
                'ru-RU' : 'Настройте комбинации устройств модулей для достижения высоких кадр/сек либо снижения нагрузки на процессор.',
                'zh-CN' : '调整模块设备的组合以实现更高的fps或更低的CPU使用率。',
                'es-ES' : 'Ajuste la combinación de dispositivos de los módulos para alcanzar un mayor número de FPS o una menor carga de CPU.',
                'it-IT' : 'Regola la combinazione dei dispositivi del modulo per ottenere fps più alti o un minore utilizzo della CPU.'},

    'QFaceMerger.face_x_offset':{
                'en-US' : 'Face X offset',
                'ru-RU' : 'Смещение лица X',
                'zh-CN' : '人脸X方向偏移',
                'es-ES' : 'Desplazamiento en X de la cara',
                'it-IT' : 'Compensazione su X della faccia'},

    'QFaceMerger.face_y_offset':{
                'en-US' : 'Face Y offset',
                'ru-RU' : 'Смещение лица Y',
                'zh-CN' : '人脸Y方向偏移',
                'es-ES' : 'Desplazamiento en Y de la cara',
                'it-IT' : 'Compensazione su Y della faccia'},

    'QFaceMerger.face_scale':{
                'en-US' : 'Face scale',
                'ru-RU' : 'Масштаб лица',
                'zh-CN' : '人脸缩放',
                'es-ES' : 'Escala de la cara',
                'it-IT' : 'Scala della faccia'},

    'QFaceMerger.face_mask_type':{
                'en-US' : 'Face mask type',
                'ru-RU' : 'Тип маски лица',
                'zh-CN' : '人脸遮罩类型',
                'es-ES' : 'Tipo de máscara de la cara',
                'it-IT' : 'Tipo di maschera della faccia'},

    'QFaceMerger.face_mask_erode':{
                'en-US' : 'Face mask erode',
                'ru-RU' : 'Укорочение маски',
                'zh-CN' : '遮罩向内缩边',
                'es-ES' : 'Máscara de erode',
                'it-IT' : 'Maschera da erodere'},

    'QFaceMerger.face_mask_blur':{
                'en-US' : 'Face mask blur',
                'ru-RU' : 'Размытие маски',
                'zh-CN' : '遮罩边缘羽化',
                'es-ES' : 'Máscara de desenfoque',
                'it-IT' : 'Maschera da sfocare'},

    'QFaceMerger.help.color_transfer':{
                'en-US' : 'Match the color distribution of the replaced face to the original face.',
                'ru-RU' : 'Совместить цветовое распределение заменённого лица с исходным.',
                'zh-CN' : '将被替换的面孔的颜色分布与原始面孔相匹配。',
                'es-ES' : 'Hacer coincidir la distribución de color del rostro reemplazado con el rostro original.',
                'it-IT' : 'Abbina la distribuzione del colore della faccia sostituita a quella della faccia originale.'},

    'QFaceMerger.color_transfer':{
                'en-US' : 'Color transfer',
                'ru-RU' : 'Перенос цвета',
                'zh-CN' : '彩色转印',
                'es-ES' : 'Transferencia de color',
                'it-IT' : 'Trasferimento di colore'},

    'QFaceMerger.interpolation':{
                'en-US' : 'Interpolation',
                'ru-RU' : 'Интерполяция',
                'zh-CN' : '插值',
                'es-ES' : 'Interpolación',
                'it-IT' : 'Interpolazione'},

    'QFaceMerger.color_compression':{
                'en-US' : 'Color compression',
                'ru-RU' : 'Сжатие цвета',
                'zh-CN' : '颜色压缩',
                'es-ES' : 'Compresión de color',
                'it-IT' : 'Compressione dei colori'},

    'QFaceMerger.face_opacity':{
                'en-US' : 'Face opacity',
                'ru-RU' : 'Непрозрач. лица',
                'zh-CN' : '人脸透明度',
                'es-ES' : 'Opacidad de la cara',
                'it-IT' : 'Opacità della faccia'},

    'QStreamOutput.module_title':{
                'en-US' : 'Stream output',
                'ru-RU' : 'Выходной поток',
                'zh-CN' : '视频流输出',
                'es-ES' : 'Flujo de salida',
                'it-IT' : 'Flusso in uscita'},

    'QStreamOutput.avg_fps':{
                'en-US' : 'Average FPS',
                'ru-RU' : 'Среднее кадр/сек',
                'zh-CN' : '平均帧率',
                'es-ES' : 'FPS promedio',
                'it-IT' : 'FPS medi'},

    'QStreamOutput.help.avg_fps':{
                'en-US' : 'Average FPS of output stream.',
                'ru-RU' : 'Среднее кадр/сек выходного стрима.',
                'zh-CN' : '输出流的平均帧率',
                'es-ES' : 'FPS promedio del flujo de salida.',
                'it-IT' : 'FPS medi del flusso in uscita.'},

    'QStreamOutput.source_type':{
                'en-US' : 'Source',
                'ru-RU' : 'Источник',
                'zh-CN' : '源',
                'es-ES' : 'Origen',
                'it-IT' : 'Sorgente'},

    'QStreamOutput.show_hide_window':{
                'en-US' : 'window',
                'ru-RU' : 'окно',
                'zh-CN' : '窗口显示',
                'es-ES' : 'ventana',
                'it-IT' : 'finestra'},

    'QStreamOutput.aligned_face_id':{
                'en-US' : 'Face ID',
                'ru-RU' : 'Номер лица',
                'zh-CN' : '人脸ID',
                'es-ES' : 'ID de cara',
                'it-IT' : 'ID faccia'},

    'QStreamOutput.help.aligned_face_id':{
                'en-US' : 'ID of aligned face to show.',
                'ru-RU' : 'Номер выровненного лица для показа.',
                'zh-CN' : '要展示的人脸ID',
                'es-ES' : 'ID de la cara alineada para mostrar.',
                'it-IT' : 'ID della faccia allineata da mostrare.'},

    'QStreamOutput.target_delay':{
                'en-US' : 'Target delay',
                'ru-RU' : 'Целев. задержка',
                'zh-CN' : '音画延迟',
                'es-ES' : 'Retraso objetivo',
                'it-IT' : 'Ritardo obiettivo'},

    'QStreamOutput.help.target_delay':{
                'en-US' : 'Target delay in milliseconds between input frame and output frame.\nMatch this value with audio delay in your stream software to get syncronized stream.',
                'ru-RU' : 'Целевая задержка в миллисекундах между входным и выходным кадрами.\nСовместите это значение с аудио задержкой в вашем стриминговом софте для получения синхронизированного потока.',
                'zh-CN' : '输入帧和输出帧之间的目标延迟（以毫秒为单位）。\n将此值与流软件中的音频延迟匹配，实现音画同步的输出流。',
                'es-ES' : 'Retraso objetivo en milisegundos entre el frame de entrada y el frame de salida.\nHaz coincidir este valor con el retraso de audio en tu software de streaming para obtener un flujo sincronizado.',
                'it-IT' : "Il ritardo obiettivo in millisecondi tra il fotogramma entrante e quello uscente.\nFai corrispondere questo valore con il ritardo audio nel tuo software di streaming per ottenere uno stream sincronizzato."},

    'QStreamOutput.save_sequence_path':{
                'en-US' : 'Save sequence',
                'ru-RU' : 'Сохр. секвенцию',
                'zh-CN' : '保存序列帧',
                'es-ES' : 'Guardar secuencia',
                'it-IT' : 'Salva sequenza'},

    'QStreamOutput.help.save_sequence_path':{
                'en-US' : 'Save image sequence of output stream to the directory.',
                'ru-RU' : 'Сохранить выходной стрим в виде набора изображений в директорию.',
                'zh-CN' : '将输出流的图像序列保存到目录中。',
                'es-ES' : 'Guardar secuencia de imágenes del flujo de salida en la carpeta.',
                'it-IT' : 'Salva la sequenza di immagini del flusso in uscita in una cartella.'},

    'QStreamOutput.save_fill_frame_gap':{
                'en-US' : 'Fill frame gap',
                'ru-RU' : 'Заполнить пустоты',
                'zh-CN' : '补帧',
                'es-ES' : 'Rellenar hueco del frame',
                'it-IT' : 'Riempi il vuoto del fotogramma'},

    'QStreamOutput.help.save_fill_frame_gap':{
                'en-US' : 'Fill frame drops by duplicating last frame.',
                'ru-RU' : 'Заполнить кадровые пустоты дубликатами последнего кадра.',
                'zh-CN' : '用最后帧来填充帧间隙',
                'es-ES' : 'Rellenar huecos del frame con duplicados del último frame.',
                'it-IT' : "Riempi la perdita di fotogrammi duplicando l'ultimo frame"},

    'QBCFrameViewer.title':{
                'en-US' : 'Source frame',
                'ru-RU' : 'Исходный кадр',
                'zh-CN' : '源画面',
                'es-ES' : 'Frame de origen',
                'it-IT' : 'Frame sorgente'},

    'QBCFaceAlignViewer.title':{
                'en-US' : 'Aligned face',
                'ru-RU' : 'Выровненное лицо',
                'zh-CN' : '对齐校正后的脸',
                'es-ES' : 'Cara alineada',
                'it-IT' : 'Faccia allineata'},

    'QBCFaceSwapViewer.title':{
                'en-US' : 'Swapped face',
                'ru-RU' : 'Заменённое лицо',
                'zh-CN' : '换后的脸',
                'es-ES' : 'Cara intercambiada'},

    'QBCMergedFrameViewer.title':{
                'en-US' : 'Merged frame',
                'ru-RU' : 'Склеенный кадр',
                'zh-CN' : '合成后的画面',
                'es-ES' : 'Frame fusionado',
                'it-IT' : 'Fotogramma fuso'},

    'FileSource.image_folder':{
                'en-US' : 'Image folder',
                'ru-RU' : 'Папка изображений',
                'zh-CN' : '图片文件夹',
                'es-ES' : 'Carpeta de imágenes',
                'it-IT' : 'Cartella immagini'},

    'FileSource.video_file':{
                'en-US' : 'Video file',
                'ru-RU' : 'Видео файл',
                'zh-CN' : '视频文件',
                'es-ES' : 'Archivo de video',
                'it-IT' : 'File video'},

    'FaceDetector.LARGEST':{
                'en-US' : 'Largest',
                'ru-RU' : 'Наибольшему',
                'zh-CN' : '最大',
                'es-ES' : 'El más grande',
                'it-IT' : 'Il più grande'},

    'FaceDetector.DIST_FROM_CENTER':{
                'en-US' : 'Dist from center',
                'ru-RU' : 'Расстоянию от центра',
                'zh-CN' : '离中心的距离',
                'es-ES' : 'Distancia desde el centro',
                'it-IT' : 'Distanza dal centro'},

    'FaceDetector.LEFT_RIGHT':{
                'en-US' : 'From left to right',
                'ru-RU' : 'Слева направо',
                'zh-CN' : '从左至右',
                'es-ES' : 'De izquierda a derecha',
                'it-IT' : 'Da sinistra a destra'},

    'FaceDetector.RIGHT_LEFT':{
                'en-US' : 'From right to left',
                'ru-RU' : 'Справа налево',
                'zh-CN' : '从右到左',
                'es-ES' : 'De derecha a izquierda',
                'it-IT' : 'Da destra a sinistra'},

    'FaceDetector.TOP_BOTTOM':{
                'en-US' : 'From top to bottom',
                'ru-RU' : 'Сверху вниз',
                'zh-CN' : '从左至右',
                'es-ES' : 'De arriba a abajo',
                'it-IT' : "Dall'alto verso il basso"},

    'FaceDetector.BOTTOM_TOP':{
                'en-US' : 'From bottom to top',
                'ru-RU' : 'Снизу вверх',
                'zh-CN' : '从下到上',
                'es-ES' : 'De abajo a arriba',
                'it-IT' : "Dal basso verso l'alto"},

    'FaceSwapper.model_information':{
                'en-US' : 'Model information',
                'ru-RU' : 'Информация о модели',
                'zh-CN' : '模型信息',
                'es-ES' : 'Información del modelo',
                'it-IT' : 'Informazioni modello'},

    'FaceSwapper.filename':{
                'en-US' : 'Filename:',
                'ru-RU' : 'Имя файла:',
                'zh-CN' : '文件名',
                'es-ES' : 'Nombre del archivo:',
                'it-IT' : 'Nome file'},

    'FaceSwapper.resolution':{
                'en-US' : 'Resolution:',
                'ru-RU' : 'Разрешение:',
                'zh-CN' : '分辨率',
                'es-ES' : 'Resolución:',
                'it-IT' : 'Risoluzione:'},

    'FaceSwapper.downloading_model':{
                'en-US' : 'Downloading model...',
                'ru-RU' : 'Загрузка модели...',
                'zh-CN' : '下载模型中...',
                'es-ES' : 'Descargando modelo...',
                'it-IT' : 'Scaricando modello...'},

    'StreamOutput.SourceType.SOURCE_FRAME':{
                'en-US' : 'Source frame',
                'ru-RU' : 'Исходный кадр',
                'zh-CN' : '源帧',
                'es-ES' : 'Frame de origen',
                'it-IT' : 'Fotogramma sorgente'},

    'StreamOutput.SourceType.ALIGNED_FACE':{
                'en-US' : 'Aligned face',
                'ru-RU' : 'Выровненное лицо',
                'zh-CN' : '对齐校正后的脸',
                'es-ES' : 'Cara alineada',
                'it-IT' : 'Faccia allineata'},

    'StreamOutput.SourceType.SWAPPED_FACE':{
                'en-US' : 'Swapped face',
                'ru-RU' : 'Заменённое лицо',
                'zh-CN' : '换后的脸',
                'es-ES' : 'Cara intercambiada'},

    'StreamOutput.SourceType.MERGED_FRAME':{
                'en-US' : 'Merged frame',
                'ru-RU' : 'Склеенный кадр',
                'zh-CN' : '合成后的画面',
                'es-ES' : 'Frame fusionado',
                'it-IT' : 'Fotogramma fuso'},

    'StreamOutput.SourceType.MERGED_FRAME_OR_SOURCE_FRAME':{
                'en-US' : 'Merged frame or source frame',
                'ru-RU' : 'Склеенный кадр или исходный кадр',
                'zh-CN' : '合成后的画面否则源帧',
                'es-ES' : 'Frame fusionado o frame de origen',
                'it-IT' : 'Fotogramma fuso o fotogramma sorgente'},

    'StreamOutput.SourceType.SOURCE_N_MERGED_FRAME':{
                'en-US' : 'Source and merged frame',
                'ru-RU' : 'Исходный и склеенный кадр',
                'zh-CN' : '源和融合后的帧',
                'es-ES' : 'Frame de origen y fusionado',
                'it-IT' : 'Fotogramma sorgente e fuso'},

    'StreamOutput.SourceType.SOURCE_N_MERGED_FRAME_OR_SOURCE_FRAME':{
                'en-US' : 'Source and merged frame or source frame',
                'ru-RU' : 'Исходный и склеенный кадр или исходный кадр',
                'zh-CN' : '源和融合后的帧则源帧',
                'es-ES' : 'Frame de origen y fusionado o frame de origen',
                'it-IT' : 'Fotogramma sorgente e fuso o fotogramma sorgente'},
    }
