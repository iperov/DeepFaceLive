import onnxruntime as rt

from .device import ORTDeviceInfo


def InferenceSession_with_device(onnx_modelpath, device_info : ORTDeviceInfo):
    """
    Construct onnxruntime.InferenceSession with this Device.

     device_info     ORTDeviceInfo

    can raise Exception
    """

    prs = rt.get_available_providers()

    if device_info.is_cpu():
        if 'CPUExecutionProvider' not in prs:
            raise Exception('CPUExecutionProvider is not avaiable in onnxruntime')
        providers = ['CPUExecutionProvider']
    else:
        if 'CUDAExecutionProvider' not in prs:
            raise Exception('CUDAExecutionProvider is not avaiable in onnxruntime')
        providers = [ ('CUDAExecutionProvider', {'device_id': device_info.get_index() }) ]
        #providers = [ ('DmlExecutionProvider', {'device_id': 1 }) ]

    sess_options = rt.SessionOptions()
    #sess_options.enable_mem_pattern = False #for DmlExecutionProvider
    sess_options.log_severity_level = 4
    sess_options.log_verbosity_level = -1
    sess = rt.InferenceSession(onnx_modelpath, providers=providers, sess_options=sess_options)
    return sess
