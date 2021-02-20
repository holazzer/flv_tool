# Flv Tool Documentation


## Reading an FLV file

```python

from flv_tool.flv_reader import FlvReader
f = open(r'your_video.flv','rb')
reader = FlvReader(f)
flv = reader.read_flv()
```

`flv` is a `FLV` object which contains all tag information in the video file you specifiy.


## Inspecting an `FLV` object 

The implementation is fairly self-explainatory, all fields in the specification can be found in `FLV` with (almost) the same name. 

An FLV file consists of blocks, like this:

```
+------------------
| FLV Header 
+------------------
| Tag[0] Size (There being no previous tag, 
|              this tag should always report size 0. )
+------------------
| Tag[1] (This tag usually is a Script Tag 
|         with name 'onMetaData', which of course 
|         contains the video's metadata. )
+------------------
| Tag[1] Size 
+------------------
| Tag[2]
+------------------
| Tag[2] Size
+------------------
| ......
```

For a binary file example, see [flv_read_example.md](../flv_read_example.md)

An `FLV` object have fields:
+ name: File name copied from the file handle 
+ header: `FlvHeader` object
+ body: `List[BaseFlvTag]` with alternating `PrevTagSize` and `FlvTag`


### `repr_verbose`

Every non-primitive field inherits from the class `BaseFlvTag`, which has the method `repr_verbose` that returns a *no-so-pretty* string representation. (I'm working on that...)

Example 1 (Header):
```python
print(flv.header.repr_verbose())
```
```
<FlvHeader [0=>9]>
version: 1
flag_audio: 1
flag_video: 1
header_length: 9
```
You can learn that header takes 9 bytes (as version 1 flv's all do), and takes up the file's bytes from 0 to 9.

Example 2 (PrevTagSize):
```python
print(flv.body[0].repr_verbose())
```

```
<PrevTagSize [9=>13]>
```

According to specification, tag1 should be a ScriptTag with name `onMetaData` and A LOT OF fields and `repr_verbose` does not work well on this one.

Example 3 (Video Tag)

```python
print(flv.body[3].repr_verbose())
```

```
<FlvTag [1402=>1465]>
filter: 0
tag_type: 9
data_size: 52
timestamp: 0
timestamp_extended: 0
video_tag_header: <VideoTagHeader [1413=>1418]>
frame_type: 1
codec_id: 7
avc_packet_type: 0
composition_time: 0

data: <BinaryData [1418=>1465]>

real_timestamp: 0
```

### `py_native_type`

The `py_native_type` method can turn almost all fields into python native date types. It is done recursively, since Adobe clearly doesn't know what it's doing.

Example 1 (Header):
```python
flv.header.py_native_value
```
```python
{'first_byte_after': 0,
 'last_byte_at': 9,
 'version': 1,
 'flag_audio': 1,
 'flag_video': 1,
 'header_length': 9}
```

Example 2 (Tag[0] Size):
```python
flv.body[0].py_native_value
```

```python
{'first_byte_after': 9, 'last_byte_at': 13, 'size': 0}
```

Example 3 (Tag[1], the `onMetaData` Script Data Tag)
```python
flv.body[1].py_native_value
```
```python
{'first_byte_after': 13,
 'last_byte_at': 1398,
 'filter': 0,
 'tag_type': <TagType.Script: 18>,
 'data_size': 1374,
 'timestamp': 0,
 'timestamp_extended': 0,
 'encryption_header': NotImplemented,
 'filter_params': NotImplemented,
 'data': {'onMetaData': {'description': 'Bilibili VXCode Swarm Transcoder r0.2.61(gap_fixed:False)',
   'metadatacreator': 'Version 1.9',
   'hasKeyframes': 1,
   'hasVideo': 1,
   'hasAudio': 1,
   'hasMetadata': 1,
   'canSeekToEnd': 1,
   'duration': 194.404,
   'datasize': 22108709.0,
   'videosize': 18833511.0,
   'framerate': 29.985532392509793,
   'videodatarate': 754.9738434280506,
   'videocodecid': 7.0,
   'width': 852.0,
   'height': 480.0,
   'audiosize': 3218422.0,
   'audiodatarate': 125.63848994876648,
   'audiocodecid': 10.0,
   'audiosamplerate': 3.0,
   'audiosamplesize': 1.0,
   'stereo': 1,
   'filesize': 22110111.0,
   'lasttimestamp': 194.227,
   'lastkeyframetimestamp': 194.227,
   'lastkeyframelocation': 22110091.0,
   'keyframes': {'filepositions': [1402.0, 1488.0, (omitted), 22110091.0],
    'times': [0.0, 0.0, (omitted), 194.227]}}},
 'real_timestamp': 0}
```


