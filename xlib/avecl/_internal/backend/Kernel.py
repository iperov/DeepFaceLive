class Kernel:
    """
    TensorCL kernel.

    It does not allocate any resources, thus can be used as static variable within class.

    arguments

        kernel_text    OpenCL text of kernel. Must contain only one __kernel

        global_shape    default global_shape for .run()

        local_shape     default local_shape for .run()
    """
    def __init__(self, kernel_text, global_shape=None, local_shape=None):
        self._kernel_text = kernel_text
        self._global_shape = global_shape
        self._local_shape = local_shape

    def get_kernel_text(self) -> str: return self._kernel_text
    def get_global_shape(self): return self._global_shape
    def get_local_shape(self): return self._local_shape

    def __str__(self):  return f'Kernel: \n{self._kernel_text}'
    def __repr__(self): return self.__str__()

