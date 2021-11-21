from enum import IntEnum


class TagType(IntEnum):
    Audio = 8
    Video = 9
    Script = 18


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


