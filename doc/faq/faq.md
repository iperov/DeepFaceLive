<table align="center" border="0">
<tr><td colspan=2 align="center">

## Do I need to train the model from scratch?

No you don't. There are public face models that can swap any face without training.

</td></tr>
<tr><td colspan=2 align="center">

## When will AMD cards be supported?

Depends on <a href="https://github.com/microsoft/onnxruntime">microsoft/onnxruntime</a> library developers. AMD cards are supported through DirectML execution provider, which is currently raw and slow.

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

Src faceset is celebrity. Must be diverse enough.

Dst faceset is RTM WF faceset from the torrent.

Make a backup before every stage !

> Using SAEHD model.

res:224, WF, ae_dims:256, e_dims:64, d_dims:64, d_mask_dims 22, eyes_mouth_prio:Y, batch 8. Others are default.
1) enable pretrain mode. Train to 1kk
2) disable pretrain mode. Train to 1kk
3) lrd:N uniform_yaw:True, color_transfer:lct, train +500..800k
4) lrd:Y train +500..800k iters
5) disable random warp +500..800k iters
6) enable gan 0.1 gan_dims:32, train +100..300k iters

You can reuse this model to train new src faceset. In this case you should to delete inter_AB.npy from model folder, and train from stage 3.

> Using AMP model.

res:224, WF, ae_dims:256, inter_dims:1024, e_dims:64, d_dims:64, d_mask_dims:22, morph factor:0.5, batch 8. Others are default.

1) lrd:Y, train src-src for 1kk iters
2) delete inter_dst, lrd:N, color_transfer:lct, train +1kk
3) lrd:Y, train +1kk
4) enable gan 0.1 gan_dims:32, train +100..300k iters

</td></tr>
</table>



