import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class FRNorm2D(nn.Module):
    def __init__(self, in_ch):
        super().__init__()
        self.in_ch = in_ch
        self.weight = nn.parameter.Parameter( torch.Tensor(1, in_ch, 1, 1), requires_grad=True)
        self.bias = nn.parameter.Parameter( torch.Tensor(1, in_ch, 1, 1), requires_grad=True)
        self.eps = nn.parameter.Parameter(torch.Tensor(1), requires_grad=True)
        nn.init.ones_(self.weight)
        nn.init.zeros_(self.bias)
        nn.init.constant_(self.eps, 1e-6)

    def forward(self, x):
        nu2 = x.pow(2).mean(dim=[2, 3], keepdim=True)
        x = x * torch.rsqrt(nu2 + self.eps.abs())
        return self.weight * x + self.bias

class TLU(nn.Module):
    def __init__(self, in_ch):
        super(TLU, self).__init__()
        self.in_ch = in_ch
        self.tau = nn.parameter.Parameter(torch.Tensor(1, in_ch, 1, 1), requires_grad=True)
        nn.init.zeros_(self.tau)

    def forward(self, x):
        return torch.max(x, self.tau)

class BlurPool(nn.Module):
    def __init__(self, in_ch, filt_size=3, stride=2, pad_off=0):
        super().__init__()
        self.in_ch = in_ch
        self.filt_size = filt_size
        self.pad_off = pad_off
        self.pad_sizes = [int(1.*(filt_size-1)/2), int(np.ceil(1.*(filt_size-1)/2)), int(1.*(filt_size-1)/2), int(np.ceil(1.*(filt_size-1)/2))]
        self.pad_sizes = [pad_size+pad_off for pad_size in self.pad_sizes]
        self.stride = stride
        self.off = int((self.stride-1)/2.)

        if(self.filt_size==2):
            a = np.array([1., 1.])
        elif(self.filt_size==3):
            a = np.array([1., 2., 1.])
        elif(self.filt_size==4):
            a = np.array([1., 3., 3., 1.])
        elif(self.filt_size==5):
            a = np.array([1., 4., 6., 4., 1.])
        elif(self.filt_size==6):
            a = np.array([1., 5., 10., 10., 5., 1.])
        elif(self.filt_size==7):
            a = np.array([1., 6., 15., 20., 15., 6., 1.])

        filt = torch.Tensor(a[:,None]*a[None,:])
        filt = filt/torch.sum(filt)
        self.register_buffer('filt', filt[None,None,:,:].repeat(in_ch,1,1,1)  )

        self.pad = nn.ZeroPad2d(self.pad_sizes)

    def forward(self, inp):
        return F.conv2d(self.pad(inp), self.filt, stride=self.stride, groups=self.in_ch)


class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Conv2d (in_ch, out_ch, kernel_size=3, padding=1)
        self.frn = FRNorm2D(out_ch)
        self.tlu = TLU(out_ch)

    def forward(self, x):
        x = self.conv(x)
        x = self.frn(x)
        x = self.tlu(x)
        return x

class UpConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.ConvTranspose2d (in_ch, out_ch, kernel_size=3, stride=2, padding=1,output_padding=1)
        self.frn = FRNorm2D(out_ch)
        self.tlu = TLU(out_ch)

    def forward(self, x):
        x = self.conv(x)
        x = self.frn(x)
        x = self.tlu(x)
        return x

class XSegNet(nn.Module):
    def __init__(self, in_ch, out_ch, base_ch=32):
        """
        
        """
        super().__init__()
        self.base_ch = base_ch

        self.conv01 = ConvBlock(in_ch, base_ch)
        self.conv02 = ConvBlock(base_ch, base_ch)
        self.bp0 = BlurPool (base_ch, filt_size=4)

        self.conv11 = ConvBlock(base_ch, base_ch*2)
        self.conv12 = ConvBlock(base_ch*2, base_ch*2)
        self.bp1 = BlurPool (base_ch*2, filt_size=3)

        self.conv21 = ConvBlock(base_ch*2, base_ch*4)
        self.conv22 = ConvBlock(base_ch*4, base_ch*4)
        self.bp2 = BlurPool (base_ch*4, filt_size=2)

        self.conv31 = ConvBlock(base_ch*4, base_ch*8)
        self.conv32 = ConvBlock(base_ch*8, base_ch*8)
        self.conv33 = ConvBlock(base_ch*8, base_ch*8)
        self.bp3 = BlurPool (base_ch*8, filt_size=2)

        self.conv41 = ConvBlock(base_ch*8, base_ch*8)
        self.conv42 = ConvBlock(base_ch*8, base_ch*8)
        self.conv43 = ConvBlock(base_ch*8, base_ch*8)
        self.bp4 = BlurPool (base_ch*8, filt_size=2)

        self.conv51 = ConvBlock(base_ch*8, base_ch*8)
        self.conv52 = ConvBlock(base_ch*8, base_ch*8)
        self.conv53 = ConvBlock(base_ch*8, base_ch*8)
        self.bp5 = BlurPool (base_ch*8, filt_size=2)

        self.dense1 = nn.Linear ( 4*4* base_ch*8, 512)
        self.dense2 = nn.Linear ( 512, 4*4* base_ch*8)

        self.up5 = UpConvBlock (base_ch*8, base_ch*4)
        self.uconv53 = ConvBlock(base_ch*12, base_ch*8)
        self.uconv52 = ConvBlock(base_ch*8, base_ch*8)
        self.uconv51 = ConvBlock(base_ch*8, base_ch*8)

        self.up4 = UpConvBlock (base_ch*8, base_ch*4)
        self.uconv43 = ConvBlock(base_ch*12, base_ch*8)
        self.uconv42 = ConvBlock(base_ch*8, base_ch*8)
        self.uconv41 = ConvBlock(base_ch*8, base_ch*8)

        self.up3 = UpConvBlock (base_ch*8, base_ch*4)
        self.uconv33 = ConvBlock(base_ch*12, base_ch*8)
        self.uconv32 = ConvBlock(base_ch*8, base_ch*8)
        self.uconv31 = ConvBlock(base_ch*8, base_ch*8)

        self.up2 = UpConvBlock (base_ch*8, base_ch*4)
        self.uconv22 = ConvBlock(base_ch*8, base_ch*4)
        self.uconv21 = ConvBlock(base_ch*4, base_ch*4)

        self.up1 = UpConvBlock (base_ch*4, base_ch*2)
        self.uconv12 = ConvBlock(base_ch*4, base_ch*2)
        self.uconv11 = ConvBlock(base_ch*2, base_ch*2)

        self.up0 = UpConvBlock (base_ch*2, base_ch)
        self.uconv02 = ConvBlock(base_ch*2, base_ch)
        self.uconv01 = ConvBlock(base_ch, base_ch)

        self.out_conv = nn.Conv2d (base_ch, out_ch, kernel_size=7, padding=3)

    def forward(self, inp):
        x = inp

        x = self.conv01(x)
        x = x0 = self.conv02(x)
        x = self.bp0(x)

        x = self.conv11(x)
        x = x1 = self.conv12(x)
        x = self.bp1(x)

        x = self.conv21(x)
        x = x2 = self.conv22(x)
        x = self.bp2(x)

        x = self.conv31(x)
        x = self.conv32(x)
        x = x3 = self.conv33(x)
        x = self.bp3(x)

        x = self.conv41(x)
        x = self.conv42(x)
        x = x4 = self.conv43(x)
        x = self.bp4(x)

        x = self.conv51(x)
        x = self.conv52(x)
        x = x5 = self.conv53(x)
        x = self.bp5(x)

        x = x.view(x.shape[0], -1)
        x = self.dense1(x)
        x = self.dense2(x)
        x = x.view (-1, self.base_ch*8, 4, 4)

        x = self.up5(x)

        x = self.uconv53(torch.cat([x,x5],axis=1))
        x = self.uconv52(x)
        x = self.uconv51(x)

        x = self.up4(x)
        x = self.uconv43(torch.cat([x,x4],axis=1))
        x = self.uconv42(x)
        x = self.uconv41(x)

        x = self.up3(x)
        x = self.uconv33(torch.cat([x,x3],axis=1))
        x = self.uconv32(x)
        x = self.uconv31(x)

        x = self.up2(x)
        x = self.uconv22(torch.cat([x,x2],axis=1))
        x = self.uconv21(x)

        x = self.up1(x)
        x = self.uconv12(torch.cat([x,x1],axis=1))
        x = self.uconv11(x)

        x = self.up0(x)
        x = self.uconv02(torch.cat([x,x0],axis=1))
        x = self.uconv01(x)

        x = self.out_conv(x)

        return x

