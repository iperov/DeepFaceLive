#!/bin/bash
# Warning xhost + is overly permissive and will reduce system security. Edit as desired
docker build . -t deepfacelive
xhost +
docker run --ipc host --gpus all -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd)/data/:/data/  --rm -it deepfacelive
