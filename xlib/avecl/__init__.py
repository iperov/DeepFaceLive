"""
AveCL ! Make OpenCL great again.

Lightweight ndarray library using OpenCL 1.2 written in pure python.
Applicable for high-performance general purpose n-dim array computations for every device that supports OpenCL 1.2.
Supports any dtype except float64.

Works in python 3.5+. Dependencies: numpy.

This lib uses relative import, thus you can place it in any subfolder.
The lib is not thread-safe.

made by @iperov from scratch.
"""

from xlib.avecl._internal.initializer.InitConst import InitConst

from ._internal.AAxes import AAxes
from ._internal.AShape import AShape
from ._internal.backend import (Device, DeviceInfo, Kernel,
                                get_available_devices_info, get_best_device,
                                get_default_device, get_device,
                                set_default_device)
from ._internal.EInterpolation import EInterpolation
from ._internal.HArgs import HArgs
from ._internal.HKernel import HKernel
from ._internal.HTensor import HTensor
from ._internal.HType import HType
from ._internal.initializer import (InitConst, InitCoords2DArange, Initializer,
                                    InitRandomUniform)
from ._internal.NCore import NCore
from ._internal.NTest import NTest
from ._internal.op import *
from ._internal.SCacheton import SCacheton
from ._internal.Tensor import Tensor
from ._internal.TensorImpl import *
