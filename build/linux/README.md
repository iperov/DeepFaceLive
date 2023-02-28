# DeepFaceLive Docker

### Requirements

* nvidia-driver>=470
* cuda>=11.4

### Setup
1. Open console and clone git repo
```
git clone https://github.com/iperov/DeepFaceLive.git
cd DeepFaceLive/build/linux/
```
1. `start.sh` builds and run container with proper options<br>
2. Usage of `./start.sh`<br>
-d specify a folder for DeepFaceLive data (videos, models, etc)<br>
`-d /home/userJohn/DeepFaceLive_data`<br>
**if data folder not specified - used data in build/linux/data<br>
***create data folder in build/linux if launch first time and no matter where to place<br>
-c will pass through existing video devices(webcam, fake webcam and other) such as /dev/video0 and /dev/video1, etc<br>
`-c /dev/video0`<br>
If no autodetect you video driver run in host(not have locate, modinfo)<br>
`nvidia-smi | grep Driver`<br>
and see output:

```
NVIDIA-SMI 525.89.02    Driver Version: 525.89.02    CUDA Version: 12.0
```

 -r bruild and run with you driver version from nvidia-smi like this <br>
 `./start.sh -r 525 -d /home/userJohn/DeepFaceLive_data -c /dev/video0`<br>
## ***DO NOT RUN `./start.sh ` from root(sudo)!
