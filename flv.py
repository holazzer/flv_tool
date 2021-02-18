"""
Flv 
"""
from abc import ABC, abstractmethod
from struct import unpack
from datetime import datetime
from enum import IntEnum

from typing import BinaryIO, Tuple, Optional, Union


class BaseReader:
    def __init__(self, f):
        self.f: BinaryIO = f

    def read_UI8(self) -> int:
        ui8 = self.f.read(1)
        return unpack("B", ui8)[0]

    def read_SI8(self) -> int:
        ui8 = self.f.read(1)
        return unpack("b", ui8)[0]

    def read_byte(self) -> bytes:
        return self.f.read(1)

    def read_UI24(self) -> int:
        b1, b2, b3 = unpack('3B', self.f.read(3))
        return (b1 << 16) + (b2 << 8) + b3

    def read_UI32(self) -> int:
        ui32 = self.f.read(4)
        return unpack(">I", ui32)[0]


class BaseFlvTag(ABC):
    pass


class FlvHeader(BaseFlvTag):
    def __init__(self):
        self.version: int = None
        self.flag_audio: bool = None
        self.flag_video: bool = None
        self.header_length: int = None


class PrevTagLength(BaseFlvTag):
    def __init__(self):
        self.prev_tag: Optional[BaseFlvTag] = None
        self.length: int = None


class TagType(IntEnum):
    audio = 8
    video = 9
    script_data = 18


class FlvTag(BaseFlvTag):
    def __init__(self):
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


class AudioTagHeader(BaseFlvTag):
    pass


class VideoTagHeader(BaseFlvTag):
    pass


class BaseData(ABC):
    pass


class AudioData(BaseData):
    pass


class VideoData(BaseData):
    pass


class ScriptData(BaseData):
    pass


