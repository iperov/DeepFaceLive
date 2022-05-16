<table align="center" border="0">

<tr><td colspan=2 align="center">

![](doc/deepfacelive_intro.png)

![](doc/logo_onnx.png)![](doc/logo_directx.png)![](doc/logo_python.png)

</td></tr>
</table>
<table align="center" border="0">

<tr><td colspan=2 align="center">

## Face Swapper

You can swap your face from a webcam or the face in the video using trained face models.

Here is a list of available ready-to-use public face models.

These persons do not exists. Similarities with real people are accidental. Except Keanu Reeves. He exists, and he's breathtaking!
</td></tr>

<tr><td colspan=2 align="center">

<table align="center" border="0">

<tr><td align="center" colspan=4>
Keanu Reeves

<img src="doc/celebs/Keanu_Reeves/Keanu_Reeves.png" width=128></img>

<a href="doc/celebs/Keanu_Reeves/examples.md">examples</a>
</td></tr>
<tr><td align="center">
Ava de Addario

<img src="doc/celebs/Ava_de_Addario/Ava_de_Addario.png" width=128></img>

<a href="doc/celebs/Ava_de_Addario/examples.md">examples</a>
</td><td align="center">
Dilraba Dilmurat

<img src="doc/celebs/Dilraba_Dilmurat/Dilraba_Dilmurat.png" width=128></img>

examples
</td><td align="center">
Ewon Spice

<img src="doc/celebs/Ewon_Spice/Ewon_Spice.png" width=128></img>

<a href="doc/celebs/Ewon_Spice/examples.md">examples</a>

</td><td align="center">
Yohanna Coralson

<img src="doc/celebs/Yohanna_Coralson/Yohanna_Coralson.png" width=128></img>

<a href="doc/celebs/Yohanna_Coralson/examples.md">examples</a>

</td></tr></table>
<table align="center" border="0">
<tr align="center"><td align="center">
Kim Jarrey

<img src="doc/celebs/Kim_Jarrey/Kim_Jarrey.png" width=128></img>

<a href="doc/celebs/Kim_Jarrey/examples.md">examples</a>
</td><td>
David Kovalniy

<img src="doc/celebs/David_Kovalniy/David_Kovalniy.png" width=128></img>

<a href="doc/celebs/David_Kovalniy/examples.md">examples</a>
</td><td>
Matilda Bobbie

<img src="doc/celebs/Matilda_Bobbie/Matilda_Bobbie.png" width=128></img>

<a href="doc/celebs/Matilda_Bobbie/examples.md">examples</a>
</td><td>
Bryan Greynolds

<img src="doc/celebs/Bryan_Greynolds/Bryan_Greynolds.png" width=128></img>

<a href="doc/celebs/Bryan_Greynolds/examples.md">examples</a>
</td><td>
Nicola Badge

<img src="doc/celebs/Nicola_Badge/Nicola_Badge.png" width=128></img>

<a href="doc/celebs/Nicola_Badge/examples.md">examples</a>
</td></tr></table>
<table align="center" border="0">
<tr align="center"><td align="center">
Silwan Stillwone

<img src="doc/celebs/Silwan_Stillwone/Silwan_Stillwone.png" width=128></img>

<a href="doc/celebs/Silwan_Stillwone/examples.md">examples</a>
</td><td>
Tim Chrys

<img src="doc/celebs/Tim_Chrys/Tim_Chrys.png" width=128></img>

<a href="doc/celebs/Tim_Chrys/examples.md">examples</a>

</td><td>
Zahar Lupin

<img src="doc/celebs/Zahar_Lupin/Zahar_Lupin.png" width=128></img>

<a href="doc/celebs/Zahar_Lupin/examples.md">examples</a>
</td><td>
Tim Norland

<img src="doc/celebs/Tim_Norland/Tim_Norland.png" width=128></img>

<a href="doc/celebs/Tim_Norland/examples.md">examples</a>
</td></tr></table>

</td></tr>

<tr><td colspan=2 align="center">
If you want a higher quality or better face match, you can train your own face model using <a href="https://github.com/iperov/DeepFaceLab">DeepFaceLab</a>

Here is an <a href="https://www.tiktok.com/@arnoldschwarzneggar/video/6995538782204300545">example</a> of Arnold Schwarzneggar trained on a particular face and used in a video call. Read the FAQ for more information.

</td></tr>

</table>
<table align="center" border="0">

<tr><td colspan=2 align="center">

## Face Animator

There is also a Face Animator module in DeepFaceLive app. You can control a static face picture using video or your own face from the camera. The quality is not the best, and requires fine face matching and tuning parameters for every face pair, but enough for funny videos and memes or real-time streaming at 25 fps using 35 TFLOPS GPU.

<img src="doc/face_animator_example.gif"></img>

Here is a [mini video](doc/FaceAnimator_tutor.webm?raw=true) showing the process of setting up the Face Animator for Obama controlling Kim Chen's face.

</td></tr>

</table>
<table align="center" border="0">

<tr><td colspan=2 align="center">

## Minimum system requirements

any DirectX12 compatible graphics card

Modern CPU with AVX instructions

4GB RAM, 32GB+ paging file

Windows 10

</td></tr>
<tr><td colspan=2 align="center">

## Setup tutorial

<tr><td colspan=2 align="center">

<a href="doc/setup_tutorial_windows/index.md">Windows 10 x64</a>

<a href="build/linux">Linux build info</a>

## Documentation

<a href="doc/user_faq/user_faq.md">User FAQ</a>

<a href="doc/developer_faq/developer_faq.md">Developer FAQ</a>

</td></tr>
<tr><td colspan=2 align="center">

## Releases

</td></tr>
<tr><td align="right">

<a href="https://disk.yandex.ru/d/7i5XTKIKVg5UUg">Windows 10 x64 (yandex.ru)</a>

<a href="https://mega.nz/folder/m10iELBK#Y0H6BflF9C4k_clYofC7yA">Windows 10 x64 (mega.nz)</a>


</td><td align="left">
Contains stand-alone zero-dependency all-in-one ready-to-use portable self-extracting folder! You don't need to install anything other than video drivers.
<br><br>
DirectX12 build : NVIDIA, AMD, Intel videocards.
<br><br>
NVIDIA build : NVIDIA cards only, GT730 and higher. Works faster than DX12. FaceMerger can work also on AMD/Intel.
</td></tr>
<tr><td colspan=2 align="center">

## Communication groups

<tr><td align="right">
<a href="https://discord.gg/S2h7kPySQp">Discord</a>
</td><td align="left">Official discord channel. English / Russian.</td></tr>

<tr><td align="right">
<a href="https://mrdeepfakes.com/forums/">mrdeepfakes</a>
</td><td align="left">the biggest NSFW English deepfake community</td></tr>

<tr><td align="right">
<a href="https://www.dfldata.xyz">dfldata.xyz</a>
</td><td align="left">中文交流论坛，免费软件教程、模型、人脸数据</td></tr>

</td></tr>
<tr><td colspan=2 align="center">

## How can I help the project?

</td></tr>
<tr><td colspan=2 align="center">
I need the computing power to train models.
<br>
If you have a free computer with 2080TI or better card with 12GB+ VRAM, you can give me remote access to it. I will train 1 model in a month. Contact me(iperov#6528) in Discord channel.
</td></tr>
<tr><td colspan=2 align="center">
Register github account and push "Star" button.
</td></tr>
<!--<tr><td colspan=2 align="center">
<a href="https://www.paypal.com/paypalme/DeepFaceLab">Donate via Paypal</a>
</td></tr>-->
<tr><td colspan=2 align="center">
<a href="https://money.yandex.ru/to/41001142318065">Donate via Yandex.Money</a>
</td></tr>
<tr><td colspan=2 align="center">
bitcoin:bc1qewl062v70rszulml3f0mjdjrys8uxdydw3v6rq
</td></tr>
<tr><td colspan=2 align="center">


<!--
    <a href="https://br-stone.online"><img src="doc/logo_barclay_stone.png"></img></a><a href="https://exmo.com"><img src="doc/logo_exmo.png"></img></a>

    presents

    <tr><td align="right">


    <a href="">Windows (magnet link)</a>
    </td><td align="center">Latest release. Use torrent client to download.</td></tr>
    </tr>
-->

</table>



