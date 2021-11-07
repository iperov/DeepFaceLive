import operator
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from xlib import math as lib_math
from xlib.file import SplittedFile
from xlib.image import ImageProcessor
from xlib.torch import TorchDeviceInfo, get_cpu_device_info


class S3FD:
    def __init__(self, device_info : TorchDeviceInfo = None ):
        if device_info is None:
            device_info = get_cpu_device_info()
        self.device_info = device_info
        
        path = Path(__file__).parent / 'S3FD.pth'
        SplittedFile.merge(path, delete_parts=False)
        
        net = self.net = S3FDNet()
        net.load_state_dict( torch.load(str(path) ))
        net.eval()

        if not device_info.is_cpu():
            net.cuda(device_info.get_index())

    def extract(self, img : np.ndarray, fixed_window, min_face_size=40):
        """

        """
        ip = ImageProcessor(img)

        if fixed_window != 0:
            fixed_window = max(64, max(1, fixed_window // 32) * 32 )
            img_scale = ip.fit_in(fixed_window, fixed_window, pad_to_target=True, allow_upscale=False)
        else:
            ip.pad_to_next_divisor(64, 64)
            img_scale = 1.0

        img = ip.ch(3).as_float32().apply( lambda img: img - [104,117,123]).get_image('NCHW')

        tensor = torch.from_numpy(img)
        if not self.device_info.is_cpu():
            tensor = tensor.cuda(self.device_info.get_index())

        batches_bbox = [x.data.cpu().numpy() for x in self.net(tensor)]

        faces_per_batch = []
        for batch in range(img.shape[0]):
            bbox = self.refine( [ x[batch] for x in batches_bbox ] )

            faces = []
            for l,t,r,b,c in bbox:
                if img_scale != 1.0:
                    l,t,r,b = l/img_scale, t/img_scale, r/img_scale, b/img_scale

                bt = b-t
                if min(r-l,bt) < min_face_size:
                    continue
                b += bt*0.1

                faces.append ( (l,t,r,b) )

            #sort by largest area first
            faces = [ [(l,t,r,b), (r-l)*(b-t) ]  for (l,t,r,b) in faces ]
            faces = sorted(faces, key=operator.itemgetter(1), reverse=True )
            faces = [ x[0] for x in faces]
            faces_per_batch.append(faces)

        return faces_per_batch


    def refine(self, olist):
        bboxlist = []
        variances = [0.1, 0.2]
        for i in range(len(olist) // 2):
            ocls, oreg = olist[i * 2], olist[i * 2 + 1]

            stride = 2**(i + 2)    # 4,8,16,32,64,128
            for hindex, windex in [*zip(*np.where(ocls[1, :, :] > 0.05))]:
                axc, ayc = stride / 2 + windex * stride, stride / 2 + hindex * stride
                score = ocls[1, hindex, windex]
                loc = np.ascontiguousarray(oreg[:, hindex, windex]).reshape((1, 4))
                priors = np.array([[axc, ayc, stride * 4, stride * 4]])
                bbox = np.concatenate((priors[:, :2] + loc[:, :2] * variances[0] * priors[:, 2:],
                                       priors[:, 2:] * np.exp(loc[:, 2:] * variances[1])), 1)
                bbox[:, :2] -= bbox[:, 2:] / 2
                bbox[:, 2:] += bbox[:, :2]
                x1, y1, x2, y2 = bbox[0]
                bboxlist.append([x1, y1, x2, y2, score])

        if len(bboxlist) != 0:
            bboxlist = np.array(bboxlist)
            bboxlist = bboxlist[ lib_math.nms(bboxlist[:,0], bboxlist[:,1], bboxlist[:,2], bboxlist[:,3], bboxlist[:,4], 0.3), : ]
            bboxlist = [x for x in bboxlist if x[-1] >= 0.5]

        return bboxlist


    @staticmethod
    def save_as_onnx(onnx_filepath):
        s3fd = S3FD()

        torch.onnx.export(s3fd.net,
                            torch.from_numpy( np.zeros( (1,3,640,640), dtype=np.float32)),
                            str(onnx_filepath),
                            verbose=True,
                            training=torch.onnx.TrainingMode.EVAL,
                            opset_version=9,
                            do_constant_folding=True,
                            input_names=['in'],
                            output_names=['cls1', 'reg1', 'cls2', 'reg2', 'cls3', 'reg3', 'cls4', 'reg4', 'cls5', 'reg5', 'cls6', 'reg6'],
                            dynamic_axes={'in' : {0:'batch_size',2:'height',3:'width'},
                                          'cls1' : {2:'height',3:'width'},
                                          'reg1' : {2:'height',3:'width'},
                                          'cls2' : {2:'height',3:'width'},
                                          'reg2' : {2:'height',3:'width'},
                                          'cls3' : {2:'height',3:'width'},
                                          'reg3' : {2:'height',3:'width'},
                                          'cls4' : {2:'height',3:'width'},
                                          'reg4' : {2:'height',3:'width'},
                                          'cls5' : {2:'height',3:'width'},
                                          'reg5' : {2:'height',3:'width'},
                                          'cls6' : {2:'height',3:'width'},
                                          'reg6' : {2:'height',3:'width'},
                                        },
                            )



class L2Norm(nn.Module):
    def __init__(self, n_channels, scale=1.0):
        super().__init__()
        self.n_channels = n_channels
        self.scale = scale
        self.eps = 1e-10
        self.weight = nn.Parameter(torch.Tensor(self.n_channels))
        self.weight.data *= 0.0
        self.weight.data += self.scale

    def forward(self, x):
        norm = x.pow(2).sum(dim=1, keepdim=True).sqrt() + self.eps
        x = x / norm * self.weight.view(1, -1, 1, 1)
        return x



class S3FDNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1_1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
        self.conv1_2 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)

        self.conv2_1 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.conv2_2 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1)

        self.conv3_1 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
        self.conv3_2 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)
        self.conv3_3 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)

        self.conv4_1 = nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1)
        self.conv4_2 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv4_3 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)

        self.conv5_1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv5_2 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv5_3 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)

        self.fc6 = nn.Conv2d(512, 1024, kernel_size=3, stride=1, padding=3)
        self.fc7 = nn.Conv2d(1024, 1024, kernel_size=1, stride=1, padding=0)

        self.conv6_1 = nn.Conv2d(1024, 256, kernel_size=1, stride=1, padding=0)
        self.conv6_2 = nn.Conv2d(256, 512, kernel_size=3, stride=2, padding=1)

        self.conv7_1 = nn.Conv2d(512, 128, kernel_size=1, stride=1, padding=0)
        self.conv7_2 = nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1)

        self.conv3_3_norm = L2Norm(256, scale=10)
        self.conv4_3_norm = L2Norm(512, scale=8)
        self.conv5_3_norm = L2Norm(512, scale=5)

        self.conv3_3_norm_mbox_conf = nn.Conv2d(256, 4, kernel_size=3, stride=1, padding=1)
        self.conv3_3_norm_mbox_loc = nn.Conv2d(256, 4, kernel_size=3, stride=1, padding=1)
        self.conv4_3_norm_mbox_conf = nn.Conv2d(512, 2, kernel_size=3, stride=1, padding=1)
        self.conv4_3_norm_mbox_loc = nn.Conv2d(512, 4, kernel_size=3, stride=1, padding=1)
        self.conv5_3_norm_mbox_conf = nn.Conv2d(512, 2, kernel_size=3, stride=1, padding=1)
        self.conv5_3_norm_mbox_loc = nn.Conv2d(512, 4, kernel_size=3, stride=1, padding=1)

        self.fc7_mbox_conf = nn.Conv2d(1024, 2, kernel_size=3, stride=1, padding=1)
        self.fc7_mbox_loc = nn.Conv2d(1024, 4, kernel_size=3, stride=1, padding=1)
        self.conv6_2_mbox_conf = nn.Conv2d(512, 2, kernel_size=3, stride=1, padding=1)
        self.conv6_2_mbox_loc = nn.Conv2d(512, 4, kernel_size=3, stride=1, padding=1)
        self.conv7_2_mbox_conf = nn.Conv2d(256, 2, kernel_size=3, stride=1, padding=1)
        self.conv7_2_mbox_loc = nn.Conv2d(256, 4, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        h = F.relu(self.conv1_1(x))
        h = F.relu(self.conv1_2(h))
        h = F.max_pool2d(h, 2, 2)

        h = F.relu(self.conv2_1(h))
        h = F.relu(self.conv2_2(h))
        h = F.max_pool2d(h, 2, 2)

        h = F.relu(self.conv3_1(h))
        h = F.relu(self.conv3_2(h))
        h = F.relu(self.conv3_3(h))
        f3_3 = h
        h = F.max_pool2d(h, 2, 2)

        h = F.relu(self.conv4_1(h))
        h = F.relu(self.conv4_2(h))
        h = F.relu(self.conv4_3(h))
        f4_3 = h
        h = F.max_pool2d(h, 2, 2)

        h = F.relu(self.conv5_1(h))
        h = F.relu(self.conv5_2(h))
        h = F.relu(self.conv5_3(h))
        f5_3 = h
        h = F.max_pool2d(h, 2, 2)

        h = F.relu(self.fc6(h))
        h = F.relu(self.fc7(h))
        ffc7 = h

        h = F.relu(self.conv6_1(h))
        h = F.relu(self.conv6_2(h))

        f6_2 = h

        h = F.relu(self.conv7_1(h))
        h = F.relu(self.conv7_2(h))
        f7_2 = h

        f3_3 = self.conv3_3_norm(f3_3)
        f4_3 = self.conv4_3_norm(f4_3)
        f5_3 = self.conv5_3_norm(f5_3)

        cls1 = self.conv3_3_norm_mbox_conf(f3_3)
        reg1 = self.conv3_3_norm_mbox_loc(f3_3)
        cls2 = self.conv4_3_norm_mbox_conf(f4_3)
        reg2 = self.conv4_3_norm_mbox_loc(f4_3)
        cls3 = self.conv5_3_norm_mbox_conf(f5_3)
        reg3 = self.conv5_3_norm_mbox_loc(f5_3)

        cls4 = self.fc7_mbox_conf(ffc7)
        reg4 = self.fc7_mbox_loc(ffc7)
        cls5 = self.conv6_2_mbox_conf(f6_2)
        reg5 = self.conv6_2_mbox_loc(f6_2)
        cls6 = self.conv7_2_mbox_conf(f7_2)
        reg6 = self.conv7_2_mbox_loc(f7_2)

        # max-out background label
        chunk = torch.chunk(cls1, 4, 1)
        bmax = torch.max(torch.max(chunk[0], chunk[1]), chunk[2])
        cls1 = torch.cat ([bmax,chunk[3]], dim=1)
        cls1, cls2, cls3, cls4, cls5, cls6 = [ F.softmax(x, dim=1) for x in [cls1, cls2, cls3, cls4, cls5, cls6] ]

        return [cls1, reg1, cls2, reg2, cls3, reg3, cls4, reg4, cls5, reg5, cls6, reg6]


