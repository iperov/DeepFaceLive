import numpy as np

from ..Tensor import Tensor
from .depthwise_conv2D import depthwise_conv2D


def gaussian_blur (input_t : Tensor, sigma, dtype=None) -> Tensor:
    """
    arguments

        input_t     Tensor(...,H,W)

        sigma       float


    """
    if sigma <= 0.0:
        return input_t.copy() 

    device = input_t.get_device()

    key = (gaussian_blur, sigma)
    kernel_t = device.get_cached_data(key)
    if kernel_t is None:
        kernel_t = Tensor.from_value( _make_gaussian_kernel(sigma, np.float32), device=device )
        device.set_cached_data(key, kernel_t)

    output_t = depthwise_conv2D(input_t, kernel_t, dtype=dtype)
    return output_t

def _make_gaussian_kernel(sigma : float, dtype):
    kernel_size = max(3, int(2 * 2 * sigma))
    if kernel_size % 2 == 0:
        kernel_size += 1
    mean = np.floor(0.5 * kernel_size)
    kernel_1d = np.array([ np.exp(-(float(x) - float(mean)) ** 2 / (2 * sigma ** 2)) for x in range(kernel_size)])
    np_kernel = np.outer(kernel_1d, kernel_1d)
    kernel = np_kernel / np.sum(np_kernel)
    return kernel.astype(dtype)
