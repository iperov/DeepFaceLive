from functools import partial
from pathlib import Path
from typing import Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from xlib.file import SplittedFile
from xlib.torch import TorchDeviceInfo, get_cpu_device_info

def _make_divisible(v: float, divisor: int, min_value = None) -> int:
    if min_value is None:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v
        
class SqueezeExcitation(nn.Module):
    def __init__( self, in_ch: int, squeeze_channels: int, activation = nn.ReLU, scale_activation = nn.Sigmoid):
        super().__init__()
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Conv2d(in_ch, squeeze_channels, 1)
        self.fc2 = nn.Conv2d(squeeze_channels, in_ch, 1)
        self.activation = activation()
        self.scale_activation = scale_activation()

    def forward(self, input):
        scale = self.avgpool(input)
        scale = self.fc1(scale)
        scale = self.activation(scale)
        scale = self.fc2(scale)
        scale = self.scale_activation(scale)
        return scale * input
        
class ConvNormActivation(nn.Sequential):
    def __init__(self, in_ch: int, out_ch: int, kernel_size: int = 3, stride: int = 1, padding = None, groups: int = 1, norm_layer = nn.BatchNorm2d, activation_layer = nn.ReLU,) -> None:
        if padding is None:
            padding = (kernel_size - 1) // 2
        layers = [torch.nn.Conv2d(in_ch, out_ch, kernel_size, stride, padding, groups=groups, bias=norm_layer is None)]
        if norm_layer is not None:
            layers.append(norm_layer(out_ch))
        if activation_layer is not None:
            layers.append(activation_layer())
        super().__init__(*layers)
        self.out_ch = out_ch
        

class InvertedResidual(nn.Module):
    def __init__(self, in_ch: int, mid_ch: int, out_ch: int, kernel: int, stride: int,  use_se: bool,
                       hs_act : bool, width_mult: float = 1.0,    
                       norm_layer = None,):
        super().__init__()
        
        mid_ch = _make_divisible(mid_ch * width_mult, 8)
        out_ch = _make_divisible(out_ch * width_mult, 8)
        self._is_res_connect = stride == 1 and in_ch == out_ch
        activation_layer = nn.Hardswish if hs_act else nn.ReLU

        layers = []

        if mid_ch != in_ch:
            layers.append(ConvNormActivation(in_ch, mid_ch, kernel_size=1, norm_layer=norm_layer, activation_layer=activation_layer))

        layers.append(ConvNormActivation(mid_ch, mid_ch, kernel_size=kernel, stride=stride, groups=mid_ch, norm_layer=norm_layer, activation_layer=activation_layer))

        if use_se:
            layers.append( SqueezeExcitation(mid_ch, _make_divisible(mid_ch // 4, 8), scale_activation=nn.Hardsigmoid) )

        layers.append(ConvNormActivation(mid_ch, out_ch, kernel_size=1, norm_layer=norm_layer, activation_layer=None))

        self.block = nn.Sequential(*layers)
        self.out_ch = out_ch

    def forward(self, input):
        result = self.block(input)
        if self._is_res_connect:
            result = result + input
        return result
          
class FaceAlignerNet(nn.Module):
    def __init__(self):
        super().__init__()
        norm_layer = partial(nn.BatchNorm2d, eps=0.001, momentum=0.01)
        
        width_mult = 1.66
        
        self.c0  = c0  = ConvNormActivation(3, _make_divisible(16 * width_mult, 8), kernel_size=3, stride=2, norm_layer=norm_layer, activation_layer=nn.Hardswish)
        self.c1  = c1  = InvertedResidual ( c0.out_ch,  16,  16,  3, 1, use_se=False, hs_act=False, norm_layer=norm_layer, width_mult=width_mult)
        self.c2  = c2  = InvertedResidual ( c1.out_ch,  64,  24,  3, 2, use_se=False, hs_act=False, norm_layer=norm_layer, width_mult=width_mult)
        self.c3  = c3  = InvertedResidual ( c2.out_ch,  72,  24,  3, 1, use_se=False, hs_act=False, norm_layer=norm_layer, width_mult=width_mult)
        self.c4  = c4  = InvertedResidual ( c3.out_ch,  72,  40,  5, 2, use_se=True,  hs_act=False, norm_layer=norm_layer, width_mult=width_mult)
        self.c5  = c5  = InvertedResidual ( c4.out_ch,  120, 40,  5, 1, use_se=True,  hs_act=False, norm_layer=norm_layer, width_mult=width_mult)
        self.c6  = c6  = InvertedResidual ( c5.out_ch,  120, 40,  5, 1, use_se=True,  hs_act=False, norm_layer=norm_layer, width_mult=width_mult)
        self.c7  = c7  = InvertedResidual ( c6.out_ch,  240, 80,  3, 2, use_se=False, hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c8  = c8  = InvertedResidual ( c7.out_ch,  200, 80,  3, 1, use_se=False, hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c9  = c9  = InvertedResidual ( c8.out_ch,  184, 80,  3, 1, use_se=False, hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c10 = c10 = InvertedResidual ( c9.out_ch,  184, 80,  3, 1, use_se=False, hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c11 = c11 = InvertedResidual ( c10.out_ch, 480, 112, 3, 1, use_se=True,  hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c12 = c12 = InvertedResidual ( c11.out_ch, 672, 112, 3, 1, use_se=True,  hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c13 = c13 = InvertedResidual ( c12.out_ch, 672, 160, 5, 2, use_se=True,  hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c14 = c14 = InvertedResidual ( c13.out_ch, 960, 160, 5, 1, use_se=True,  hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c15 = c15 = InvertedResidual ( c14.out_ch, 960, 160, 5, 1, use_se=True,  hs_act=True,  norm_layer=norm_layer, width_mult=width_mult)
        self.c16 = c16 = ConvNormActivation(c15.out_ch, _make_divisible(6*160*width_mult, 8), kernel_size=1, norm_layer=norm_layer, activation_layer=nn.Hardswish)
        
        self.fc1 = nn.Linear(c16.out_ch, _make_divisible(c16.out_ch*1.33, 8))
        self.fc1_act = nn.Hardswish()
        self.fc2 = nn.Linear(self.fc1.out_features, 4)
        
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)
                
    def forward(self, inp):
        x = inp     
        
        x = self.c0(x)
        x = self.c1(x)
        x = self.c2(x)
        x = self.c3(x)
        x = self.c4(x)
        x = self.c5(x)
        x = self.c6(x)
        x = self.c7(x)
        x = self.c8(x)
        x = self.c9(x)
        x = self.c10(x)
        x = self.c11(x)
        x = self.c12(x)
        x = self.c13(x)
        x = self.c14(x)
        x = self.c15(x)
        x = self.c16(x)
        
        x = x.mean((-2,-1))
        x = self.fc1(x)
        x = self.fc1_act(x)
        
        x = self.fc2(x)
        
        scale_t, angle_t, tx_t, ty_t = torch.split(x, 1, -1)
        
        aff_t = torch.cat([torch.cos(angle_t)*scale_t, -torch.sin(angle_t)*scale_t, tx_t,
                           torch.sin(angle_t)*scale_t,  torch.cos(angle_t)*scale_t, ty_t,
                          ], dim=-1).view(-1,2,3)
        
        return aff_t

