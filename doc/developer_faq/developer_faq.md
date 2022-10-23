<table align="center" border="0">
<tr><td colspan=2 align="center">

## Why Python for such high load software and not C++?

All CPU-intensive tasks are done by native libraries compiled for Python, such as OpenCV, NumPy, PyQt, onnxruntime. Python is more like a command processor that tells what to do. All you need is to organize such commands properly.
  (Above information is not necessary accurate. Especially for Windows platform. Asyncronous IO is very well designed at Windows kernell, can'ty say the same about POSIX async IO in Linux... So, Python GIL is smart, and in most cases it is not blocking process/thread, if you call OS native IO libraries, despite being single threaded by a design, IO work is executed by OS in multithread manner. But, there is alway one but, Python performance is really degraded when it comes to dispatching callbacks from kernel IO, and perforance is really degraded comparing to C++ or even Java and C#. Having all that said, I am not saying that Python is a wrong choice here, there is no that much IO in this project - I suspect 95% of work is CPU/GPU bound. Knowing Python's simplicity, I belevei it was right choice. And I think this project is state of the art product, thanks)

## What does the internal architecture look like?

<img src="architecture.png"></img>

It consists of backend modules that work in separate processes. The modules work like a conveyor belt. CameraSource(FileSource) generates the frame and sends it to the next module for processing, so the final FPS is equal to the FPS of the slowest module. The final output module outputs the stream to the screen with the desired delay, which helps to synchronize the sound. Backend modules manage the abstract controls that are implemented in the UI. Thus, the Model-View-Controller pattern is implemented. To reduce latency, some custom interprocess communication elements are implemented directly in Python.

## How many people were involved in the development? 

Just me. It took eight months from scratch until the first release.

</td></tr>
</table>



