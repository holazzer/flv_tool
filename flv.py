"""
Flv Tool
"""
from struct import unpack
from datetime import datetime
from enum import IntEnum

from typing import BinaryIO, Tuple, Optional, Union, List


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
        return unpack('>i', b1 + b2 + b3 + b4)[0]

    def read_byte(self) -> bytes:
        return self.f.read(1)

    def read_UI24(self) -> int:
        b1, b2, b3 = unpack('3B', self.f.read(3))
        return (b1 << 16) + (b2 << 8) + b3

    def read_UI32(self) -> int:
        ui32 = self.f.read(4)
        return unpack(">I", ui32)[0]


class BaseFlvTag:
    def __init__(self):
        self.first_byte_after: int = None
        self.last_byte_at: int = None

    @property
    def tag_size(self) -> int:
        if self.first_byte_after and self.last_byte_at:
            return self.last_byte_at - self.first_byte_after
        return -1


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
    audio = 8
    video = 9
    script_data = 18


class FlvTag(BaseFlvTag):
    def __init__(self):
        super().__init__()

        # Protocol Fields
        self.filter: bool = None
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
    G711ALawLogarithmicPCM = 7   # reserved
    G711MuLawLogarithmicPCM = 8  # reserved
    reserved = 9
    AAC = 10
    Speex = 11
    MP3_8kHz = 14                # reserved
    DeviceSpecificSound = 15     # reserved


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


class VideoData(BaseData):
    pass


class AudioData(BaseData):
    pass


class ScriptData(BaseData):
    pass


class FLV:
    def __init__(self):
        self.name: str = None
        self.header: FlvHeader = FlvHeader()
        self.body: List[BaseFlvTag] = []


class FlvReader(BaseReader):
    def __init__(self, f):
        super(FlvReader, self).__init__(f)
        self.flv: FLV = None

    def read_flv(self) -> FLV:
        self.flv = FLV()
        self.flv.name = self.f.name
        self.read_flv_header()
        self.read_flv_body()
        return self.flv

    def read_flv_header(self):
        header = self.flv.header
        header.first_byte_at = self.f.tell()

        sig = self.f.read(3)
        assert sig == b'FLV', "Not a valid FLV file."
        header.version = self.read_UI8()
        one = self.read_UI8()
        # mask:  R:reserved A:audio present V:video present
        #          always 0         RRRRRARV
        header.flag_audio =(one & 0b00000100) >> 2
        header.flag_video = one & 0b00000001
        header.header_length = self.read_UI32()

        header.last_byte_at = self.f.tell()

    def read_flv_body(self):
        pass

    def read_flv_tag(self):
        tag = FlvTag()
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
        ...

    def read_flv_prev_tag_size(self):
        pts = PrevTagSize()
        pts.size = self.read_UI32()
        if self.flv.body:
            prev_tag = self.flv.body[-1]
            pts.prev_tag = prev_tag
            assert prev_tag.tag_size == pts.size , "Mismatch Prev Tag Size"
        else:
            assert pts.size == 0, "First Pre Tag Size not 0"

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
                    "AVCPacketType = {} but CompositionTime = {}, not 0."\
                    .format(header.avc_packet_type, header.composition_time)
        header.last_byte_at = self.f.tell()
        return header

    def read_video_data(self) -> VideoData:
        pass

    def read_audio_data(self) -> AudioData:
        pass

    def read_script_data(self) -> ScriptData:
        pass

