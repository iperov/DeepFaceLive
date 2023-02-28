FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

ARG NV_VER
ARG LIVE_GID="100"
ARG LIVE_UID="1000"
ARG LIVE_USER="live"

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV DEEPFACELIVE_PATH=/usr/local/deepfacelive
ENV DEEPFACELIVE_DATA=/usr/local/deepfacelive_data


RUN apt-get update --fix-missing
RUN apt-get -y install --no-install-recommends \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 \
    locales \
    sudo \
    curl \
    ffmpeg \
    git \
#    nano \
    gnupg2 \
    libsm6 \
    wget \
    unzip \
    libxcb-icccm4 \
    libxkbcommon-x11-0 \
    libxcb-keysyms1 \
    libxcb-icccm4 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-image0 \
    libnvidia-compute-${NV_VER}

RUN apt-get install -y --no-install-recommends \
    python3 \
    python3-distutils \
    python3-pyqt5

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

ENV LIVE_GID=${LIVE_GID} \
    LIVE_UID=${LIVE_UID} \
    LIVE_USER=${LIVE_USER} \
    HOME=/home/${LIVE_USER} \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    SHELL=/bin/bash

RUN echo "auth requisite pam_deny.so" >> /etc/pam.d/su \
    && sed -i.bak -e 's/^%admin/#%admin/' /etc/sudoers \
    && sed -i.bak -e 's/^%sudo/#%sudo/' /etc/sudoers \
    && useradd -m -s /bin/bash -N -u ${LIVE_UID} ${LIVE_USER} \
    && chmod g+w /etc/passwd

RUN mkdir -p ${DEEPFACELIVE_PATH} \
    && chown ${LIVE_UID}:${LIVE_GID} ${DEEPFACELIVE_PATH} \
    && mkdir -p ${DEEPFACELIVE_DATA} \
    && chown ${LIVE_UID}:${LIVE_GID} ${DEEPFACELIVE_DATA}

# Switch to user "live"
USER ${LIVE_UID}
WORKDIR ${HOME}

ENV PATH=${HOME}/.local/bin:$PATH

RUN python -c "from urllib.request import urlopen; \
    exec(urlopen('https://bootstrap.pypa.io/get-pip.py').read())"

RUN python -m pip install \
    onnxruntime-gpu==1.13.1 \
    numpy==1.21.6 \
    h5py \
    numexpr \
    protobuf==3.20.2 \
    opencv-python==4.7.0.68 \
    opencv-contrib-python==4.7.0.68 \
    pyqt6==6.4.0 \
    onnx==1.13.0 \
    torch==1.10.0 \
    torchvision==0.11.1

RUN git clone https://github.com/iperov/DeepFaceLive.git ${DEEPFACELIVE_PATH}

RUN ln -s ${DEEPFACELIVE_PATH} ${HOME}/deepfacelive \
    && ln -s ${DEEPFACELIVE_DATA} ${HOME}/deepfacelive_data

USER root

RUN apt-get --purge -y remove wget curl git \
    && apt-get --purge -y autoremove \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

USER $LIVE_UID
WORKDIR ${HOME}
CMD [ "python", "/usr/local/deepfacelive/main.py", "run", "DeepFaceLive", "--userdata-dir", "/usr/local/deepfacelive_data" ]
