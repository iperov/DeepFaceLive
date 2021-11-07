from pathlib import Path
from typing import Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from xlib.file import SplittedFile
from xlib.torch import TorchDeviceInfo, get_cpu_device_info


class ResBlock(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.conv1 = nn.Conv2d(ch, ch, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(ch, ch, kernel_size=3, stride=1, padding=1)
        
    def forward(self, inp):
        x = inp
        x = F.leaky_relu(self.conv1(x), 0.2)
        x = F.leaky_relu(self.conv2(x) + inp, 0.2)
        return x
        
class AutoEncoder(nn.Module):
    def __init__(self, resolution, in_ch, ae_ch):
        super().__init__()
        self._resolution = resolution
        self._in_ch = in_ch
        self._ae_ch = ae_ch
        
        self.conv1 = nn.Conv2d(in_ch*1, in_ch*2, kernel_size=5, stride=2, padding=2)
        self.conv2 = nn.Conv2d(in_ch*2, in_ch*4, kernel_size=5, stride=2, padding=2)
        self.conv3 = nn.Conv2d(in_ch*4, in_ch*8, kernel_size=5, stride=2, padding=2)
        self.conv4 = nn.Conv2d(in_ch*8, in_ch*8, kernel_size=5, stride=2, padding=2)
        
        self.dense_in = nn.Linear( in_ch*8 * ( resolution // (2**4) )**2, ae_ch)
        self.dense_out = nn.Linear( ae_ch, in_ch*8 * ( resolution // (2**4) )**2 )
        
        self.up_conv4 = nn.ConvTranspose2d(in_ch*8, in_ch*8, kernel_size=3, stride=2, padding=1, output_padding=(1,1), )
        self.up_conv3 = nn.ConvTranspose2d(in_ch*8, in_ch*4, kernel_size=3, stride=2, padding=1, output_padding=(1,1), )
        self.up_conv2 = nn.ConvTranspose2d(in_ch*4, in_ch*2, kernel_size=3, stride=2, padding=1, output_padding=(1,1), )
        self.up_conv1 = nn.ConvTranspose2d(in_ch*2, in_ch*1, kernel_size=3, stride=2, padding=1, output_padding=(1,1), )
        
        
    def forward(self, inp):
        x = inp
        x = F.leaky_relu(self.conv1(x), 0.1)
        x = F.leaky_relu(self.conv2(x), 0.1)
        x = F.leaky_relu(self.conv3(x), 0.1)
        x = F.leaky_relu(self.conv4(x), 0.1)
        
        x = x.view( (x.shape[0], np.prod(x.shape[1:])) )
        
        x = self.dense_in(x)
        x = self.dense_out(x)
        
        x = x.view( (x.shape[0], self._in_ch*8, self._resolution // (2**4), self._resolution // (2**4)  ))
        x = F.leaky_relu(self.up_conv4(x), 0.1)
        x = F.leaky_relu(self.up_conv3(x), 0.1)
        x = F.leaky_relu(self.up_conv2(x), 0.1)
        x = F.leaky_relu(self.up_conv1(x), 0.1)
        
        # from xlib.console import diacon
        # diacon.Diacon.stop()
        # import code
        # code.interact(local=dict(globals(), **locals()))
        
        
        return x
        
        
class CTSOTNet(nn.Module):
    def __init__(self, resolution, in_ch=6, inner_ch=64, ae_ch=256, out_ch=3, res_block_count = 12):
        super().__init__()
        self.in_conv = nn.Conv2d(in_ch, inner_ch, kernel_size=1, stride=1, padding=0)
        self.ae = AutoEncoder(resolution, inner_ch, ae_ch)
        self.out_conv = nn.Conv2d(inner_ch, out_ch, kernel_size=1, stride=1, padding=0)

    def forward(self, img1_t, img2_t):
        x = torch.cat([img1_t, img2_t], dim=1)
                
        x = self.in_conv(x)
        
        x = self.ae(x)
        x = self.out_conv(x)
        x = torch.tanh(x)
        return x



class CTSOT:
    def __init__(self, device_info : TorchDeviceInfo = None, 
                       state_dict : Union[dict, None] = None, 
                       training : bool = False):
        if device_info is None:
            device_info = get_cpu_device_info()
        self.device_info = device_info
            
        self._net = net = CTSOTNet()
        
        if state_dict is not None:
            net.load_state_dict(state_dict)
        
        if training:
            net.train()
        else:
            net.eval()
            
        self.set_device(device_info)
    
    def set_device(self, device_info : TorchDeviceInfo = None):
        if device_info is None or device_info.is_cpu():
            self._net.cpu()
        else:
            self._net.cuda(device_info.get_index())
        
    def get_state_dict(self):
        return self.net.state_dict()
        
    def get_net(self) -> CTSOTNet:
        return self._net