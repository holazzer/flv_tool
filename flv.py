"""
Flv Tool, early impl

* Do not handle encryption! (yet)
 (Do people still use that? After all, Adobe successfully killed Flash.)
 ( Will Adobe please release the source code for flash, since you paid
     big price on it and threw it like trash (what's wrong with u)? )
"""
from struct import unpack, pack
from datetime import datetime, tzinfo
from enum import IntEnum

from typing import BinaryIO, Tuple, Optional, Union, List, Iterable


class BaseReader:
    def __init__(self, f):
        self.f: BinaryIO = f

    def read_UI8(self) -> int:
        ui8 = self.f.read(1)
        return unpack("B", ui8)[0]

    def read_SI8(self) -> int:
        ui8 = self.f.read(1)
        return unpack("b", ui8)[0]

    def read_SI24(self) -> int:
        b2, b3, b4 = self.f.read(3)
        b1 = b2 & 0b10000000
        b2 = b2 & 0b01111111
        return unpack('>i', pack('4B', b1, b2, b3, b4))[0]

    def read_byte(self) -> bytes:
        return self.f.read(1)

    def read_UI24(self) -> int:
        b1, b2, b3 = unpack('3B', self.f.read(3))
        return (b1 << 16) + (b2 << 8) + b3

    def read_UI32(self) -> int:
        ui32 = self.f.read(4)
        return unpack(">I", ui32)[0]

    def read_double(self) -> float:
        ui64 = self.f.read(8)
        return unpack(">d", ui64)[0]

    def read_UI16(self) -> int:
        ui16 = self.f.read(2)
        return unpack(">H", ui16)[0]

    def read_SI16(self) -> int:
        ui16 = self.f.read(2)
        return unpack(">h", ui16)[0]

    def read_string_no_term(self, length) -> str:
        s = self.f.read(length)
        return s.decode(encoding='utf-8')


class BaseFlvTag:
    def __init__(self):
        self.first_byte_after: int = None
        self.last_byte_at: int = None

    @property
    def tag_size(self) -> int:
        if self.first_byte_after and self.last_byte_at:
            return self.last_byte_at - self.first_byte_after
        return -1

    def repr_verbose(self) -> str:
        s = "<{} [{}=>{}]>\n".format(self.__class__.__name__,
                                       self.first_byte_after,
                                       self.last_byte_at)
        for k, v in self.__dict__.items():
            ss = ''
            if (k in ['first_byte_after',
                      'last_byte_at',
                      'prev_tag',
                      'size']) \
                or (v in [None,
                          NotImplemented]):
                continue
            else:
                if isinstance(v, BaseFlvTag):
                    v = v.repr_verbose()
                ss = "{}: {}\n".format(k, v)
            s += ss
        return s

    @property
    def py_native_value(self):
        d = {}
        for k,v in self.__dict__.items():
            if v is None: continue
            if hasattr(v, 'py_native_value'):
                d[k] = v.py_native_value
            else:
                d[k] = v
        return d


class FlvHeader(BaseFlvTag):
    def __init__(self):
        super().__init__()
        self.version: int = None
        self.flag_audio: int = None
        self.flag_video: int = None
        self.header_length: int = None


class PrevTagSize(BaseFlvTag):
    def __init__(self):
        super().__init__()
        self.prev_tag: Optional[BaseFlvTag] = None
        self.size: int = None


class TagType(IntEnum):
    Audio = 8
    Video = 9
    Script = 18


class FlvTag(BaseFlvTag):
    def __init__(self):
        super().__init__()

        # Protocol Fields
        self.filter: int = None
        self.tag_type: TagType = None
        self.data_size: int = None
        self.timestamp: bytes = None
        self.timestamp_extended: bytes = None
        self.audio_tag_header: Optional[AudioTagHeader] = None
        self.video_tag_header: Optional[VideoTagHeader] = None
        self.encryption_header = NotImplemented
        self.filter_params = NotImplemented
        self.data: BaseData = None

        # Calculated Fields
        self.real_timestamp: int = None


class SoundFormat(IntEnum):
    LinearPCMPlatformEndian = 0
    ADPCM = 1
    MP3 = 2
    LinearPCMLittleEndian = 3
    Nellymoser16kHzMono = 4
    Nellymoser8kHzMono = 5
    Nellymoser = 6
    G711ALawLogarithmicPCM = 7  # reserved
    G711MuLawLogarithmicPCM = 8  # reserved
    reserved = 9
    AAC = 10
    Speex = 11
    MP3_8kHz = 14  # reserved
    DeviceSpecificSound = 15  # reserved


class SoundRate(IntEnum):
    SoundRate_5_5_kHz = 0
    SoundRate_11_kHz = 1
    SoundRate_22_kHz = 2
    SoundRate_44_kHz = 3


class SoundSize(IntEnum):
    SoundSize_8_bit_sample = 0
    SoundSize_16_bit_sample = 1


class SoundType(IntEnum):
    MonoSound = 0
    StereoSound = 1


class AACPacketType(IntEnum):
    AAC_SequenceHeader = 0
    AAC_Raw = 1


class AudioTagHeader(BaseFlvTag):
    def __init__(self):
        super().__init__()
        self.sound_format: SoundFormat = None
        self.sound_rate: SoundRate = None
        self.sound_size: SoundSize = None
        self.sound_type: SoundType = None
        self.aac_packet_type: Optional[AACPacketType] = None


class FrameType(IntEnum):
    KeyFrame = 1
    InterFrame = 2
    DisposableInterFrame = 3
    GeneratedKeyFrame = 4
    VideoInfo_CommandFrame = 5


class CodecID(IntEnum):
    SorensonH263 = 2
    ScreenVideo = 3
    On2VP6 = 4
    On2VP6_with_alpha = 5
    ScreenVideoV2 = 6
    AVC = 7


class AVCPacketType(IntEnum):
    AVC_SequenceHeader = 0
    AVC_NALU = 1
    AVC_EndOfSeq = 2


class VideoTagHeader(BaseFlvTag):
    def __init__(self):
        super().__init__()
        self.frame_type: FrameType = None
        self.codec_id: CodecID = None
        self.avc_packet_type: Optional[AVCPacketType] = None
        self.composition_time: Optional[int] = None


class BaseData(BaseFlvTag):
    pass


class BinaryData(BaseData):
    pass


class ValueType(IntEnum):
    Number = 0
    Boolean = 1
    String = 2
    Object = 3
    MovieClip = 4  # not supported, but still warms an old flash developer's heart ;)
    Null = 5
    Undefined = 6  # Did you know that AS3 was the only impl of ES4 ?
    Reference = 7
    ECMA_array = 8
    Object_end_marker = 9
    StrictArray = 10
    Date = 11
    LongString = 12


class ScriptDataValue(BaseData):
    def __init__(self):
        super().__init__()
        self.type: ValueType = None
        self.script_data_value: Union[float, int,
                                      ScriptDataString, ScriptDataObject, ScriptDataECMAArray,
                                      ScriptDataStrictArray, ScriptDataDate, ScriptDataLongString] = None

    @property
    def py_native_value(self):  # return python native representation
        if self.type in (0, 1, 7):
            return self.script_data_value
        else:
            return self.script_data_value.py_native_value


class ScriptDataDate(BaseData):
    def __init__(self):
        super().__init__()
        self.date_time: float = None  # unix timestamp value
        self.local_date_time_offset: int = None

    @property
    def real_datetime(self):
        return datetime.fromtimestamp(self.date_time)


class ScriptDataECMAArray(BaseData):
    def __init__(self):
        super().__init__()
        self.array_length: int = None  # *approximate* length
        self.variables: List[ScriptDataObjectProperty] = []
        # list terminator omitted

    @property
    def py_native_value(self):
        d = {}
        d.update(i.py_native_value for i in self.variables)
        return d


class ScriptDataLongString(BaseData):
    def __init__(self):
        super().__init__()
        self.string_length: int = None  # string_date length in bytes
        self.string_data: str = None

    @property
    def py_native_value(self):
        return self.string_data


class ScriptDataObject(BaseData):
    def __init__(self):
        super().__init__()
        self.object_properties: List[ScriptDataObjectProperty] = []
        # list terminator omitted

    @property
    def py_native_value(self):
        d = {}
        d.update(i.py_native_value for i in self.object_properties)
        return d


class ScriptDataObjectProperty(BaseData):
    def __init__(self):
        super().__init__()
        self.property_name: ScriptDataString = None
        self.property_data: ScriptDataValue = None

    @property
    def py_native_value(self):
        return (self.property_name.py_native_value,
                self.property_data.py_native_value)


class ScriptDataStrictArray(BaseData):
    def __init__(self):
        super().__init__()
        self.strict_array_length: int = None  # Number of items
        self.strict_array_value: List[ScriptDataValue] = []

    @property
    def py_native_value(self):
        return [i.py_native_value for i in self.strict_array_value]


class ScriptDataString(BaseData):
    def __init__(self):
        super().__init__()
        self.string_length: int = None
        self.string_data: str = None

    @property
    def py_native_value(self):
        return self.string_data


class ScriptData(BaseData):
    def __init__(self):
        super().__init__()
        self.name: ScriptDataValue = None
        self.value: ScriptDataValue = None

    @property
    def py_native_value(self):
        return {self.name.py_native_value: self.value.py_native_value }


class FLV:
    def __init__(self):
        self.name: str = None
        self.header: FlvHeader = FlvHeader()
        self.body: List[BaseFlvTag] = []


class FlvReader(BaseReader):
    def __init__(self, f):
        super(FlvReader, self).__init__(f)
        self.flv: FLV = None
        self.file_length = self.f.seek(0, 2)
        self.f.seek(0)

    def read_flv(self) -> FLV:
        self.flv = FLV()
        self.flv.name = self.f.name
        self.read_flv_header()
        self.read_flv_body()
        return self.flv

    def read_flv_header(self):
        header = self.flv.header
        header.first_byte_after = self.f.tell()
        sig = self.f.read(3)
        assert sig == b'FLV', "Not a valid FLV file."
        header.version = self.read_UI8()
        one = self.read_UI8()
        header.flag_audio = (one & 0b00000100) >> 2
        header.flag_video = one & 0b00000001
        header.header_length = self.read_UI32()
        header.last_byte_at = self.f.tell()

    def read_flv_body(self):
        while 1:
            if self.f.tell() < self.file_length:
                self.read_flv_prev_tag_size()
            else:
                break
            if self.f.tell() < self.file_length:
                self.read_flv_tag()
            else:
                break

    def read_flv_tag(self):
        tag = FlvTag()
        self.flv.body.append(tag)
        tag.first_byte_after = self.f.tell()

        one = self.read_UI8()
        tag.filter = (one & 0b00100000) >> 5
        tag.tag_type = TagType(one & 0b00011111)
        tag.data_size = self.read_UI24()

        tag.timestamp = self.read_UI24()
        tag.timestamp_extended = self.read_UI8()
        tag.real_timestamp = \
            (tag.timestamp_extended << 24) | tag.timestamp

        stream_id = self.read_UI24()
        assert stream_id == 0, "StreamID not 0"

        data_size_start = self.f.tell()

        if tag.tag_type == 8:
            tag.audio_tag_header = self.read_audio_tag_header()
        if tag.tag_type == 9:
            tag.video_tag_header = self.read_video_tag_header()
        if tag.filter == 1:
            raise NotImplementedError("Encryption Not Implemented yet")
        if tag.tag_type == 8 or tag.tag_type == 9:
            tag.data = BinaryData()
            tag.data.first_byte_after = self.f.tell()
            tag.data.last_byte_at = data_size_start + tag.data_size
            self.f.seek(tag.data.last_byte_at)
        elif tag.tag_type == 18:
            tag.data = self.read_script_data()

        tag.last_byte_at = self.f.tell()

    def read_flv_prev_tag_size(self):
        pts = PrevTagSize()
        pts.first_byte_after = self.f.tell()
        pts.size = self.read_UI32()
        if self.flv.body:
            prev_tag = self.flv.body[-1]
            pts.prev_tag = prev_tag
            assert prev_tag.tag_size == pts.size, "Mismatch Prev Tag Size"
        else:
            assert pts.size == 0, "First Pre Tag Size not 0"
        pts.last_byte_at = self.f.tell()
        self.flv.body.append(pts)

    def read_audio_tag_header(self) -> AudioTagHeader:
        header = AudioTagHeader()
        header.first_byte_after = self.f.tell()
        one = self.read_UI8()
        header.sound_format = SoundFormat((one & 0b11110000) >> 4)
        header.sound_rate = SoundRate((one & 0b00001100) >> 2)
        header.sound_size = SoundSize((one & 0b00000010) >> 1)
        header.sound_type = SoundType((one & 0b00000001))
        if header.sound_format == 10:
            header.aac_packet_type = AACPacketType(self.read_UI8())
        header.last_byte_at = self.f.tell()
        return header

    def read_video_tag_header(self) -> VideoTagHeader:
        header = VideoTagHeader()
        header.first_byte_after = self.f.tell()
        one = self.read_UI8()
        header.frame_type = FrameType((one & 0b11110000) >> 4)
        header.codec_id = CodecID((one & 0b00001111))
        if header.codec_id == 7:
            header.avc_packet_type = AVCPacketType(self.read_UI8())
            header.composition_time = self.read_SI24()
            if header.avc_packet_type != 1:
                assert header.composition_time == 0, \
                    "AVCPacketType = {} but CompositionTime = {}, not 0." \
                        .format(header.avc_packet_type, header.composition_time)
        header.last_byte_at = self.f.tell()
        return header

    def read_script_data(self) -> ScriptData:
        script = ScriptData()
        script.first_byte_after = self.f.tell()
        script.name = self.read_script_data_value()
        script.value = self.read_script_data_value()
        script.last_byte_at = self.f.tell()
        return script

    def read_script_data_value(self) -> ScriptDataValue:
        value = ScriptDataValue()
        value.first_byte_after = self.f.tell()
        value.type = ValueType(self.read_UI8())

        # Using Magic Numbers because specification uses them
        if value.type == 0:
            value.script_data_value = self.read_double()
        elif value.type == 1:
            value.script_data_value = self.read_UI8()
        elif value.type == 2:
            value.script_data_value = self.read_script_data_string()
        elif value.type == 3:
            value.script_data_value = self.read_script_data_object()
        elif value.type == 7:
            value.script_data_value = self.read_UI16()
        elif value.type == 8:
            value.script_data_value = self.read_script_data_ecma_array()
        elif value.type == 10:
            value.script_data_value = self.read_script_data_strict_array()
        elif value.type == 11:
            value.script_data_value = self.read_script_data_date()
        elif value.type == 12:
            value.script_data_value = self.read_script_data_long_string()

        value.last_byte_at = self.f.tell()
        return value

    def read_script_data_date(self) -> ScriptDataDate:
        sdd = ScriptDataDate()
        sdd.first_byte_after = self.f.tell()
        sdd.date_time = self.read_double()
        sdd.local_date_time_offset = self.read_UI16()
        sdd.last_byte_at = self.f.tell()
        return sdd

    def read_script_data_ecma_array(self) -> ScriptDataECMAArray:
        array = ScriptDataECMAArray()
        array.first_byte_after = self.f.tell()
        array.array_length = self.read_UI32()

        # The specification says `ECMAArrayLength` is
        # `*Approximate* number of items in ECMA array`,
        # hence the `peek` method.
        while not self.peek_script_data_object_end():
            op = self.read_script_data_object_property()
            array.variables.append(op)

        self.read_script_data_object_end()
        array.last_byte_at = self.f.tell()
        return array

    def read_script_data_object_end(self):
        b = unpack("3B", self.f.read(3))
        assert b == (0, 0, 9), "Incorrect Object End Marker"

    def peek_script_data_object_end(self) -> bool:
        # `peek` may return more or less than 3 bytes
        # https://bugs.python.org/issue5811
        # e.g. buffer_size = 8192, and you're at 8190,
        #      when you peek(3), you only get 2
        # Therefore, I'll go with more expensive approach
        # should `peek` fail.
        b = self.f.peek(3)
        if len(b) == 3:
            return unpack('3B', b) == (0, 0, 9)
        else:
            b = self.f.read(3)
            self.f.seek(-3, 1)  # whence = 1 SEEK_CUR
            return unpack('3B', b) == (0, 0, 9)

    def read_script_data_long_string(self) -> ScriptDataLongString:
        ls = ScriptDataLongString()
        ls.first_byte_after = self.f.tell()
        ls.string_length = self.read_UI32()
        ls.string_data = self.read_string_no_term(ls.string_length)
        ls.last_byte_at = self.f.tell()
        return ls

    def read_script_data_object(self) -> ScriptDataObject:
        o = ScriptDataObject()
        o.first_byte_after = self.f.tell()

        while not self.peek_script_data_object_end():
            op = self.read_script_data_object_property()
            o.object_properties.append(op)
        self.read_script_data_object_end()

        o.last_byte_at = self.f.tell()
        return o

    def read_script_data_object_property(self) -> ScriptDataObjectProperty:
        op = ScriptDataObjectProperty()
        op.first_byte_after = self.f.tell()
        op.property_name = self.read_script_data_string()
        op.property_data = self.read_script_data_value()
        op.last_byte_at = self.f.tell()
        return op

    def read_script_data_strict_array(self) -> ScriptDataStrictArray:
        sa = ScriptDataStrictArray()
        sa.first_byte_after = self.f.tell()

        sa.strict_array_length = self.read_UI32()
        for _ in range(sa.strict_array_length):
            v = self.read_script_data_value()
            sa.strict_array_value.append(v)

        sa.last_byte_at = self.f.tell()
        return sa

    def read_script_data_string(self) -> ScriptDataString:
        s = ScriptDataString()
        s.first_byte_after = self.f.tell()
        s.string_length = self.read_UI16()
        s.string_data = self.read_string_no_term(s.string_length)
        s.last_byte_at = self.f.tell()
        return s
