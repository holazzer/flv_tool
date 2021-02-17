# Parsing FLV: an example

解析FLV文件的一个例子。

use `od` in a linux shell and print the binary data, where each hex value represents one byte.

在Linux命令行中，使用od命令，以十六进制表示单字节的形式表示出flv文件

```sh
$ od -t x1z --endian=big video.flv | head -n 100 > flv_head.txt
```

What it looks like (the first 6 lines):
```
Offset  XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX  >.Printable.Char.<
```
```
0000000 46 4c 56 01 05 00 00 00 09 00 00 00 00 12 00 01  >FLV.............<
0000020 62 00 00 00 00 00 00 00 02 00 0a 6f 6e 4d 65 74  >b..........onMet<
0000040 61 44 61 74 61 08 00 00 00 0f 00 05 77 69 64 74  >aData.......widt<
0000060 68 00 40 9e 00 00 00 00 00 00 00 06 68 65 69 67  >h.@.........heig<
0000100 68 74 00 40 90 e0 00 00 00 00 00 00 0d 76 69 64  >ht.@.........vid<
0000120 65 6f 64 61 74 61 72 61 74 65 00 40 ae 84 80 00  >eodatarate.@....<
```

### Prerequisites 重要前提

FLV uses **big endian**.  FLV使用**大端**表示。
```
[UI32: 300](0x12C) => 01 2C 
```

**The following plain text is best viewed with enough window width for one line (75 characters).** 建议在足够宽的窗口下阅读。


Refer to the flv specification when you have trouble with my markings. 对我的记号有疑惑时，请参阅 flv specification.


### Header
```
        [--------header----------] [ 4 Bytes ] [TAG1 start--> 
0000000 46 4c 56 01 05 00 00 00 09 00 00 00 00 12 00 01  >FLV.............<
        8] 8] 8] 8] 8] [32 offset] R  R  R  R  
        F  L  V  v1 ||     9 Byte      
                 00000101
                 RRRRRARV
        R-reserved A-audio V-video 
```


### Tag 1
```
                                               [TAG1 start--> 
0000000 46 4c 56 01 05 00 00 00 09 00 00 00 00 12 00 01  >FLV.............<
                                               || [==3B=>>
                                            00010010
                                            RRFTTTTT  
                                            F - filtered  1 bit
                                            [0: unencrypted]
                                            T - Tag Type  5 bit
                                            8 = audio 01000
                                            9 = video 01001
                                            18=script 10010 

0000020 62 00 00 00 00 00 00 00 02 00 0a 6f 6e 4d 65 74  >b..........onMet<
        =] [timestamp] StreamID [script data start ====>
  size=354 [      ] [] RRRRRRRR   lasts for 354 Bytes 
            UI24   UI8            last byte at: 394 B
    UI8(high)+UI24(low) => SI32   tag length: 354+11=365

0000040 61 44 61 74 61 08 00 00 00 0f 00 05 77 69 64 74  >aData.......widt<
0000060 68 00 40 9e 00 00 00 00 00 00 00 06 68 65 69 67  >h.@.........heig<
0000100 68 74 00 40 90 e0 00 00 00 00 00 00 0d 76 69 64  >ht.@.........vid<
0000120 65 6f 64 61 74 61 72 61 74 65 00 40 ae 84 80 00  >eodatarate.@....<
0000140 00 00 00 00 09 66 72 61 6d 65 72 61 74 65 00 40  >.....framerate.@<
0000160 3e 00 00 00 00 00 00 00 0c 76 69 64 65 6f 63 6f  >>........videoco<
0000200 64 65 63 69 64 00 40 1c 00 00 00 00 00 00 00 0d  >decid.@.........<
0000220 61 75 64 69 6f 64 61 74 61 72 61 74 65 00 40 5f  >audiodatarate.@_<
0000240 40 00 00 00 00 00 00 0f 61 75 64 69 6f 73 61 6d  >@.......audiosam<
0000260 70 6c 65 72 61 74 65 00 40 e5 88 80 00 00 00 00  >plerate.@.......<
0000300 00 0f 61 75 64 69 6f 73 61 6d 70 6c 65 73 69 7a  >..audiosamplesiz<
0000320 65 00 40 30 00 00 00 00 00 00 00 06 73 74 65 72  >e.@0........ster<
0000340 65 6f 01 01 00 0c 61 75 64 69 6f 63 6f 64 65 63  >eo....audiocodec<
0000360 69 64 00 40 24 00 00 00 00 00 00 00 08 66 69 6c  >id.@$........fil<
0000400 65 53 69 7a 65 02 00 01 30 00 0d 61 75 64 69 6f  >eSize...0..audio<
0000420 63 68 61 6e 6e 65 6c 73 02 00 01 32 00 11 64 79  >channels...2..dy<
0000440 5f 70 75 73 68 65 72 5f 76 65 72 73 69 6f 6e 02  >_pusher_version.<
0000460 00 05 31 2e 33 2e 33 00 19 44 6f 75 79 75 54 56  >..1.3.3..DouyuTV<
0000500 42 72 6f 61 64 63 61 73 74 65 72 56 65 72 73 69  >BroadcasterVersi<
0000520 6f 6e 02 00 09 35 2e 32 2e 34 2e 31 30 30 00 07  >on...5.2.4.100..<
0000540 65 6e 63 6f 64 65 72 02 00 0d 4c 61 76 66 35 38  >encoder...Lavf58<
0000560 2e 32 30 2e 31 30 30 00 00 09 00 00 01 6d 08 00  >.20.100......m..<
==================================>>] [tag1 size] [tag2==>
                                   size=365(0x16d) 
```
```
This video was downloaded from douyu.com, a Chinese Live Streaming Website.
You can see that it contains certain field names with "DouyuTV". 
Bilibili also has this. However, Youtube uses mp4 files.

这里使用的视频是从斗鱼下载的，你可以在里面看到有DouyuTV的字段。
B站上下载的视频也有Bilibili字段。Youtube没有这玩意。因为它用的是mp4.
```

### Tag 2

```
0000560 2e 32 30 2e 31 30 30 00 00 09 00 00 01 6d 08 00  >.20.100......m..<
                                                  || [size
                                               00001000
                                               RRRTTTTT 
                                                8=audio
0000600 00 07 d5 0a 49 00 00 00 00 af 00 12 10 56 e5 00  >....I........V..<
     size=7 ] [timestamp] StreamID || [] [AACAUDIODATA]
                                   || AACPacketType
                                   || 0 = AAC sequence header
                                   || 
                                10101111
                                FFFFRRST
                                F: format  10 => AAC
                                R: rate    3 => 44kHz
                                S: size    1 => 16 bit
                                T: Type    1 => Stereo
```

### Tag 3

```
0000620 00 00 00 12 09 00 00 32 d5 0a 49 00 00 00 00 17  >.......2..I.....<
     [size:11+7=18] || [size=50][timestamp] StreamID ||
                  9=video                         00010111
                                                  FFFFCCCC
                                                  F: FrameType 1=> key frame
                                                  C: codec     7=> AVC 

0000640 00 00 00 00 01 64 00 28 ff e1 00 1d 67 64 00 28  >.....d.(....gd.(<
        || [ SI32 ] [Video Tag Body: AVC VIDEO PACKET ==>
 AVCPacket CompTime 
 0=>header         

0000660 ac d1 00 78 02 27 e5 9a 80 86 80 a0 00 00 03 00  >...x.'..........<
0000700 20 00 00 fa 01 e3 06 22 40 01 00 04 68 eb ef 2c  > ......"@...h..,<
0000720 01 00 00 00 3d 09 03 60 2a d5 0a 49 00 00 00 00  >....=..`*..I....<
====end=>] [ size=61 ] ||
                      9=video
```

The rest of the file is omitted. 剩余的文件不再展示。

