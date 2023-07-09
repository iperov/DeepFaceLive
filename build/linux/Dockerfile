FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04
WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive
ARG NV_VER
RUN apt update
RUN apt -y install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 curl ffmpeg git nano gnupg2 libsm6 wget unzip libxcb-icccm4 libxkbcommon-x11-0 libxcb-keysyms1 libxcb-icccm4 libxcb-render0 libxcb-render-util0 libxcb-image0
RUN apt install -y python3 python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN git clone https://github.com/iperov/DeepFaceLive.git

RUN python -m pip install --upgrade pip
RUN python -m pip install onnxruntime-gpu==1.15.1 numpy==1.21.6 h5py numexpr protobuf==3.20.1 opencv-python==4.8.0.74 opencv-contrib-python==4.8.0.74 pyqt6==6.5.1 onnx==1.14.0 torch==1.13.1 torchvision==0.14.1

RUN apt install -y libnvidia-compute-$NV_VER

WORKDIR /app/DeepFaceLive
COPY example.sh example.sh
CMD ./example.sh
