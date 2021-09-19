<table align="center" border="0">
<tr><td colspan=2 align="center">

## Why does it require a graphic accelerator to work?

The program is based on machine learning models. For example, face detection in the frame, facial point detection, face replacement. These models require intensive computations, which graphical accelerator can handle tens of times faster than on an ordinary processor. 

## How to increase the quality of the picture?

Play with different program settings, try different lighting in the room, a different camera angle.

## Why doesn't the replaced face look like a celebrity?

It depends on how much your face fits the shape of the celebrity's face.

## Why is the swapped face blurrier than the rest of the image?

It depends on how big the face in the frame, as well as the resolution of the model. The public models have a resolution of 224x224 to work on most PC configurations. For high face resolution, you need to train your own model. Public models are suitable for game streamers that have their face in a small window in the corner of the screen.

## Can I play at the same time as DeepFaceLive is running?

It depends on how powerful your computer and how demanding the game to resources. A multi-core processor and a separate graphics card for face replacement are recommended.

## How to increase the performance of face replacement?

Play with different program settings. Any module put on the CPU will consume a lot of CPU time, which is not enough to run a game, for example. If the motherboard allows, you can install additional video cards and distribute the load on them. I also suggest watching the CPU load in Task Manager while experimenting with the settings.


## Will DeepFake detectors be able to detect a fake in my streams?

depends on final quality of your picture. Flickering face, abruptly clipping face mask, irregular color will increase chance to detect the fake.

deepware.ai detects no fakes in the example video of the fake Margot Robbie.

<img src="deepware_result.png"></img>

## Do I need to train the model from scratch?

No you don't. There are public face models that can swap any face without training.

</td></tr>
<tr><td colspan=2 align="center">

## I want to have more control when changing faces in a video. Will the new functionality be implemented?

No. DeepFaceLive is designed for face swapping in streams. The ability to change faces in the videos - only for test purposes.

</td></tr>
<tr><td colspan=2 align="center">

## I want to swap my face to a particular celebrity. What I need to do?

This is the normal deepfake training process, where src faceset is the celebrity and dst faceset is your faceset. Train the deepfake model as usual with DeepFaceLab, then export the model in .dfm format for use in DeepFaceLive. You can also try ordering a deepfake model from someone in Discord or forum.

</td></tr>
<tr><td colspan=2 align="center">

## I want to train ready-to-use face model to swap any face to celebrity. What I need to do?

</td></tr>
<tr><td colspan=2 align="left">

If you are familiar with DeepFaceLab, then this tutorial will help you:

Src faceset is celebrity. Must be diverse enough in yaw, light and shadow conditions.
Src faceset should be xseg'ed and applied. You can apply Generic XSeg to src faceset.

Dst faceset is RTM WF faceset from the torrent.

Make a backup before every stage !

> Using SAEHD model.

-- coming soon --

> Using AMP model.

-- coming soon --


</td></tr>
</table>



