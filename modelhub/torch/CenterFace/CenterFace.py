from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def CenterFace_to_onnx(onnx_filepath):
    """Convert Pytorch CenterFace model to ONNX"""
    pth_file = Path(__file__).parent / 'CenterFace.pth'
    if not pth_file.exists():
        raise Exception(f'{pth_file} does not exist.')

    net = CenterFaceNet()
    net.load_state_dict( torch.load(pth_file) )

    torch.onnx.export(net,
                      torch.from_numpy( np.zeros( (1,3,640,640), dtype=np.float32)),
                      str(onnx_filepath),
                      verbose=True,
                      training=torch.onnx.TrainingMode.TRAINING,
                      opset_version=12,
                      do_constant_folding=False,
                      input_names=['in'],
                      output_names=['heatmap','scale','offset'],
                      dynamic_axes={'in' : {0:'batch_size',2:'height',3:'width'},
                                    'heatmap' : {2:'height',3:'width'},
                                    'scale' : {2:'height',3:'width'},
                                    'offset' : {2:'height',3:'width'},
                                    },
                      )



# class BatchNorm2D(nn.Module):
#     def __init__(self, num_features, momentum=0.1, eps=1e-5):
#         super().__init__()

#         self.num_features = num_features
#         self.momentum = momentum
#         self.eps = 1e-5

#         self.weight = nn.Parameter(torch.Tensor(num_features))
#         self.bias = nn.Parameter(torch.Tensor(num_features))
#         self.register_buffer('running_mean', torch.zeros(num_features))
#         self.register_buffer('running_var', torch.ones(num_features))
#         self.register_buffer('num_batches_tracked', torch.tensor(0, dtype=torch.long))

#     def forward(self, input : torch.Tensor):
#         input_mean = input.mean([0,2,3], keepdim=True)
#         v = input-input_mean
#         var = (v*v).mean([0,2,3], keepdim=True)


#         return self.weight.view([1, self.num_features, 1, 1]) * v / (var + self.eps).sqrt() \
#                + self.bias.view([1, self.num_features, 1, 1])

class CenterFaceNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_363 = nn.Conv2d(3, 32, 3, stride=2, padding=1, bias=False)
        self.bn_364 = nn.BatchNorm2d(32)

        self.dconv_366 = nn.Conv2d(32, 32, 3, padding=1, groups=32, bias=False)
        self.bn_367 = nn.BatchNorm2d(32)
        self.conv_369 = nn.Conv2d(32, 16, 1, padding=0, bias=False)
        self.bn_370 = nn.BatchNorm2d(16)

        self.conv_371 = nn.Conv2d(16, 96, 1, padding=0, bias=False)
        self.bn_372 = nn.BatchNorm2d(96)
        self.dconv_374 = nn.Conv2d(96, 96, 3, stride=2, padding=1, groups=96, bias=False)
        self.bn_375 = nn.BatchNorm2d(96)
        self.conv_377 = nn.Conv2d(96, 24, 1, padding=0, bias=False)
        self.bn_378 = nn.BatchNorm2d(24)

        self.conv_379 = nn.Conv2d(24, 144, 1, padding=0, bias=False)
        self.bn_380 = nn.BatchNorm2d(144)
        self.dconv_382 = nn.Conv2d(144, 144, 3, padding=1, groups=144, bias=False)
        self.bn_383 = nn.BatchNorm2d(144)
        self.conv_385 = nn.Conv2d(144, 24, 1, padding=0, bias=False)
        self.bn_386 = nn.BatchNorm2d(24)
        self.conv_388 = nn.Conv2d(24, 144, 1, padding=0, bias=False)
        self.bn_389 = nn.BatchNorm2d(144)
        self.dconv_391 = nn.Conv2d(144, 144, 3, stride=2, padding=1, groups=144, bias=False)
        self.bn_392 = nn.BatchNorm2d(144)
        self.conv_394 = nn.Conv2d(144, 32, 1, padding=0, bias=False)
        self.bn_395 = nn.BatchNorm2d(32)
        self.conv_396 = nn.Conv2d(32, 192, 1, padding=0, bias=False)
        self.bn_397 = nn.BatchNorm2d(192)
        self.dconv_399 = nn.Conv2d(192, 192, 3, padding=1, groups=192, bias=False)
        self.bn_400 = nn.BatchNorm2d(192)
        self.conv_402 = nn.Conv2d(192, 32, 1, padding=0, bias=False)
        self.bn_403 = nn.BatchNorm2d(32)
        self.conv_405 = nn.Conv2d(32, 192, 1, padding=0, bias=False)
        self.bn_406 = nn.BatchNorm2d(192)
        self.dconv_408 = nn.Conv2d(192, 192, 3, padding=1, groups=192, bias=False)
        self.bn_409 = nn.BatchNorm2d(192)
        self.conv_411 = nn.Conv2d(192, 32, 1, padding=0, bias=False)
        self.bn_412 = nn.BatchNorm2d(32)
        self.conv_414 = nn.Conv2d(32, 192, 1, padding=0, bias=False)
        self.bn_415 = nn.BatchNorm2d(192)
        self.dconv_417 = nn.Conv2d(192, 192, 3, stride=2, padding=1, groups=192, bias=False)
        self.bn_418 = nn.BatchNorm2d(192)
        self.conv_420 = nn.Conv2d(192, 64, 1, padding=0, bias=False)
        self.bn_421 = nn.BatchNorm2d(64)
        self.conv_422 = nn.Conv2d(64, 384, 1, padding=0, bias=False)
        self.bn_423 = nn.BatchNorm2d(384)
        self.dconv_425 = nn.Conv2d(384, 384, 3, padding=1, groups=384, bias=False)
        self.bn_426 = nn.BatchNorm2d(384)
        self.conv_428 = nn.Conv2d(384, 64, 1, padding=0, bias=False)
        self.bn_429 = nn.BatchNorm2d(64)
        self.conv_431 = nn.Conv2d(64, 384, 1, padding=0, bias=False)
        self.bn_432 = nn.BatchNorm2d(384)
        self.dconv_434 = nn.Conv2d(384, 384, 3, padding=1, groups=384, bias=False)
        self.bn_435 = nn.BatchNorm2d(384)
        self.conv_437 = nn.Conv2d(384, 64, 1, padding=0, bias=False)
        self.bn_438 = nn.BatchNorm2d(64)
        self.conv_440 = nn.Conv2d(64, 384, 1, padding=0, bias=False)
        self.bn_441 = nn.BatchNorm2d(384)
        self.dconv_443 = nn.Conv2d(384, 384, 3, padding=1, groups=384, bias=False)
        self.bn_444 = nn.BatchNorm2d(384)
        self.conv_446 = nn.Conv2d(384, 64, 1, padding=0, bias=False)
        self.bn_447 = nn.BatchNorm2d(64)

        self.conv_449 = nn.Conv2d(64, 384, 1, padding=0, bias=False)
        self.bn_450 = nn.BatchNorm2d(384)
        self.dconv_452 = nn.Conv2d(384, 384, 3, padding=1, groups=384, bias=False)
        self.bn_453 = nn.BatchNorm2d(384)
        self.conv_455 = nn.Conv2d(384, 96, 1, padding=0, bias=False)
        self.bn_456 = nn.BatchNorm2d(96)

        self.conv_457 = nn.Conv2d(96, 576, 1, padding=0, bias=False)
        self.bn_458 = nn.BatchNorm2d(576)
        self.dconv_460 = nn.Conv2d(576, 576, 3, padding=1, groups=576, bias=False)
        self.bn_461 = nn.BatchNorm2d(576)
        self.conv_463 = nn.Conv2d(576, 96, 1, padding=0, bias=False)
        self.bn_464 = nn.BatchNorm2d(96)

        self.conv_466 = nn.Conv2d(96, 576, 1, padding=0, bias=False)
        self.bn_467 = nn.BatchNorm2d(576)
        self.dconv_469 = nn.Conv2d(576, 576, 3, padding=1, groups=576, bias=False)
        self.bn_470 = nn.BatchNorm2d(576)
        self.conv_472 = nn.Conv2d(576, 96, 1, padding=0, bias=False)
        self.bn_473 = nn.BatchNorm2d(96)

        self.conv_475 = nn.Conv2d(96, 576, 1, padding=0, bias=False)
        self.bn_476 = nn.BatchNorm2d(576)
        self.dconv_478 = nn.Conv2d(576, 576, 3, stride=2, padding=1, groups=576, bias=False)
        self.bn_479 = nn.BatchNorm2d(576)
        self.conv_481 = nn.Conv2d(576, 160, 1, padding=0, bias=False)
        self.bn_482 = nn.BatchNorm2d(160)

        self.conv_483 = nn.Conv2d(160, 960, 1, padding=0, bias=False)
        self.bn_484 = nn.BatchNorm2d(960)
        self.dconv_486 = nn.Conv2d(960, 960, 3, padding=1, groups=960, bias=False)
        self.bn_487 = nn.BatchNorm2d(960)
        self.conv_489 = nn.Conv2d(960, 160, 1, padding=0, bias=False)
        self.bn_490 = nn.BatchNorm2d(160)

        self.conv_492 = nn.Conv2d(160, 960, 1, padding=0, bias=False)
        self.bn_493 = nn.BatchNorm2d(960)
        self.dconv_495 = nn.Conv2d(960, 960, 3, padding=1, groups=960, bias=False)
        self.bn_496 = nn.BatchNorm2d(960)
        self.conv_498 = nn.Conv2d(960, 160, 1, padding=0, bias=False)
        self.bn_499 = nn.BatchNorm2d(160)

        self.conv_501 = nn.Conv2d(160, 960, 1, padding=0, bias=False)
        self.bn_502 = nn.BatchNorm2d(960)
        self.dconv_504 = nn.Conv2d(960, 960, 3, padding=1, groups=960, bias=False)
        self.bn_505 = nn.BatchNorm2d(960)
        self.conv_507 = nn.Conv2d(960, 320, 1, padding=0, bias=False)
        self.bn_508 = nn.BatchNorm2d(320)

        self.conv_509 = nn.Conv2d(320, 24, 1, padding=0, bias=False)
        self.bn_510 = nn.BatchNorm2d(24)

        self.conv_512 = nn.ConvTranspose2d(24, 24, 2, stride=2, padding=0, bias=False)
        self.bn_513 = nn.BatchNorm2d(24)

        self.conv_515 = nn.Conv2d(96, 24, 1, padding=0, bias=False)
        self.bn_516 = nn.BatchNorm2d(24)

        self.conv_519 = nn.ConvTranspose2d(24,24, 2, stride=2, padding=0, bias=False)
        self.bn_520 = nn.BatchNorm2d(24)

        self.conv_522 = nn.Conv2d(32, 24, 1, padding=0, bias=False)
        self.bn_523 = nn.BatchNorm2d(24)

        self.conv_526 = nn.ConvTranspose2d(24,24, 2, stride=2, padding=0, bias=False)
        self.bn_527 = nn.BatchNorm2d(24)

        self.conv_529 = nn.Conv2d(24, 24, 1, padding=0, bias=False)
        self.bn_530 = nn.BatchNorm2d(24)

        self.conv_533 = nn.Conv2d(24, 24, 3, padding=1, bias=False)
        self.bn_534 = nn.BatchNorm2d(24)

        self.conv_536 = nn.Conv2d(24, 1, 1)
        self.conv_538 = nn.Conv2d(24, 2, 1)
        self.conv_539 = nn.Conv2d(24, 2, 1)
        self.conv_540 = nn.Conv2d(24, 10, 1)


    def forward(self, x):
        x = self.conv_363(x)
        x = self.bn_364(x)

        x = F.relu(x)

        x = self.dconv_366(x)
        x = self.bn_367(x)
        x = F.relu(x)
        x = self.conv_369(x)
        x = self.bn_370(x)

        x = self.conv_371(x)
        x = self.bn_372(x)
        x = F.relu(x)
        x = self.dconv_374(x)
        x = self.bn_375(x)
        x = F.relu(x)
        x = self.conv_377(x)
        x = x378 = self.bn_378(x)
        x = self.conv_379(x)
        x = self.bn_380(x)
        x = F.relu(x)
        x = self.dconv_382(x)
        x = self.bn_383(x)
        x = F.relu(x)
        x = self.conv_385(x)
        x = self.bn_386(x)
        x = x387 = x + x378
        x = self.conv_388(x)
        x = self.bn_389(x)
        x = F.relu(x)
        x = self.dconv_391(x)
        x = self.bn_392(x)
        x = F.relu(x)
        x = self.conv_394(x)
        x = x395 = self.bn_395(x)
        x = self.conv_396(x)
        x = self.bn_397(x)
        x = F.relu(x)
        x = self.dconv_399(x)
        x = self.bn_400(x)
        x = F.relu(x)
        x = self.conv_402(x)
        x = self.bn_403(x)
        x = x404 = x + x395
        x = self.conv_405(x)
        x = self.bn_406(x)
        x = F.relu(x)
        x = self.dconv_408(x)
        x = self.bn_409(x)
        x = F.relu(x)
        x = self.conv_411(x)
        x = self.bn_412(x)
        x = x413 = x + x404
        x = self.conv_414(x)
        x = self.bn_415(x)
        x = F.relu(x)
        x = self.dconv_417(x)
        x = self.bn_418(x)
        x = F.relu(x)
        x = self.conv_420(x)
        x = x421 = self.bn_421(x)
        x = self.conv_422(x)
        x = self.bn_423(x)
        x = F.relu(x)
        x = self.dconv_425(x)
        x = self.bn_426(x)
        x = F.relu(x)
        x = self.conv_428(x)
        x = self.bn_429(x)
        x = x430 = x + x421
        x = self.conv_431(x)
        x = self.bn_432(x)
        x = F.relu(x)
        x = self.dconv_434(x)
        x = self.bn_435(x)
        x = F.relu(x)
        x = self.conv_437(x)
        x = self.bn_438(x)
        x = x439 = x + x430

        x = self.conv_440(x)
        x = self.bn_441(x)
        x = F.relu(x)
        x = self.dconv_443(x)
        x = self.bn_444(x)
        x = F.relu(x)
        x = self.conv_446(x)
        x = self.bn_447(x)
        x = x + x439

        x = self.conv_449(x)
        x = self.bn_450(x)
        x = F.relu(x)
        x = self.dconv_452(x)
        x = self.bn_453(x)
        x = F.relu(x)
        x = self.conv_455(x)
        x = x456 = self.bn_456(x)

        x = self.conv_457(x)
        x = self.bn_458(x)
        x = F.relu(x)
        x = self.dconv_460(x)
        x = self.bn_461(x)
        x = F.relu(x)
        x = self.conv_463(x)
        x = self.bn_464(x)

        x = x465 = x + x456

        x = self.conv_466(x)
        x = self.bn_467(x)
        x = F.relu(x)
        x = self.dconv_469(x)
        x = self.bn_470(x)
        x = F.relu(x)
        x = self.conv_472(x)
        x = self.bn_473(x)

        x = x474 = x + x465

        x = self.conv_475(x)
        x = self.bn_476(x)
        x = F.relu(x)
        x = self.dconv_478(x)
        x = self.bn_479(x)
        x = F.relu(x)
        x = self.conv_481(x)
        x = x482 = self.bn_482(x)

        x = self.conv_483(x)
        x = self.bn_484(x)
        x = F.relu(x)
        x = self.dconv_486(x)
        x = self.bn_487(x)
        x = F.relu(x)
        x = self.conv_489(x)
        x = self.bn_490(x)

        x = x491 = x + x482

        x = self.conv_492(x)
        x = self.bn_493(x)
        x = F.relu(x)
        x = self.dconv_495(x)
        x = self.bn_496(x)
        x = F.relu(x)
        x = self.conv_498(x)
        x = self.bn_499(x)

        x = x + x491

        x = self.conv_501(x)
        x = self.bn_502(x)
        x = F.relu(x)
        x = self.dconv_504(x)
        x = self.bn_505(x)
        x = F.relu(x)
        x = self.conv_507(x)
        x = self.bn_508(x)

        x = self.conv_509(x)
        x = self.bn_510(x)
        x = F.relu(x)

        x = self.conv_512(x)
        x = self.bn_513(x)
        x = x514 = F.relu(x)

        x = self.conv_515(x474)
        x = self.bn_516(x)
        x = F.relu(x)

        x = x + x514

        x = self.conv_519(x)
        x = self.bn_520(x)
        x = x521 = F.relu(x)

        x = self.conv_522(x413)
        x = self.bn_523(x)
        x = F.relu(x)

        x = x + x521

        x = self.conv_526(x)
        x = self.bn_527(x)
        x = x528 = F.relu(x)

        x = self.conv_529(x387)
        x = self.bn_530(x)
        x = F.relu(x)

        x = x + x528

        x = self.conv_533(x)
        x = self.bn_534(x)
        x = F.relu(x)

        heatmap = torch.sigmoid( self.conv_536(x) )
        scale = self.conv_538(x)
        offset = self.conv_539(x)

        return heatmap, scale, offset
