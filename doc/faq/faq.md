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

AMP model settings: 
224 res, WF, AE 256, inter 1024, e_dims 64, d_dims 64, d_mask_dims 22, morph factor 0.5, batch 8. Others by default.

Make a backup before every stage !

1) lrd:Y, train src-src for 1kk iters
2) delete inter_dst, lrd:N, color_transfer:lct, train +1kk
3) lrd:Y, train +1kk
4) enable GAN 1.0, train +200k

</td></tr>
</table>



