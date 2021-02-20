from datetime import datetime
from typing import Optional, Union, List

from flv_tool.flv_enums import TagType, SoundFormat, SoundRate, SoundSize, SoundType, AACPacketType, FrameType, CodecID, \
    AVCPacketType, ValueType


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


class AudioTagHeader(BaseFlvTag):
    def __init__(self):
        super().__init__()
        self.sound_format: SoundFormat = None
        self.sound_rate: SoundRate = None
        self.sound_size: SoundSize = None
        self.sound_type: SoundType = None
        self.aac_packet_type: Optional[AACPacketType] = None


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