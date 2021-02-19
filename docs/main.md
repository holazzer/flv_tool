# Flv Tool Documentation


### Reading an FLV file

```python
from flv import FlvReader
f = open(r'your_video.flv','rb')
reader = FlvReader(f)
flv = reader.read_flv()
```

`flv` is a `FLV` object which contains all tag information in the video file you specifiy with.

### class `FLV` 

The implementation is fairly self-explainatory...

Every field inherits from the class `BaseFlvTag`, which has the method `repr_verbose` that returns a no-so-pretty string representation.

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


```python
print(flv.body[0].repr_verbose())
```

```
<PrevTagSize [9=>13]>
```

According to specification, tag1 should be a ScriptTag with name `onMetaData` and A LOT OF fields.


```python
print(flv.body[2].repr_verbose())
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


