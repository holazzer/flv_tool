"""
Flv Tool, early impl

* Do not handle encryption! (yet)
 (Do people still use that? After all, Adobe successfully killed Flash.)
 ( Will Adobe please release the source code for flash, since you paid
     big price on it and threw it like trash (what's wrong with u)? )
"""

from typing import List, OrderedDict as _OrderedDict, Any, Union
from flv_tool.flv_tags import BaseFlvTag, FlvHeader, PrevTagSize
from io import BytesIO
from collections import OrderedDict

from flv_tool.flv_tags import \
    PrevTagSize, FlvTag, \
    FlvHeader, BaseFlvTag, \
    AudioTagHeader, VideoTagHeader, \
    BinaryData,\
    ScriptDataValue, \
    ScriptDataDate, \
    ScriptDataECMAArray, \
    ScriptDataLongString, \
    ScriptDataObject, \
    ScriptDataObjectProperty, \
    ScriptDataStrictArray, \
    ScriptDataString, \
    ScriptData

from flv_tool.flv_enums import TagType, FrameType


class FLV:
    def __init__(self):
        self.name: str = None
        self.header: FlvHeader = FlvHeader()
        self.body: List[BaseFlvTag] = []
        self.f: BytesIO = None

    def fix_stream_flv(self):
        keyframes = self.find_key_frames()

        # note: we only need the number of keyframes to
        # determine extra bytes needed

        # calculate offset
        len_kf = len(keyframes)

        # onMetaData is an `ECMA_array`,
        # where each item is a `ObjectProperty`
        # name is a 'DataString' len = 2 Bytes (str len) + len(str)
        # value is a 'DataValue' len =
        # double - 8 Bytes [0]
        # Boolean - 1 Byte (UI8) [1]
        # String - len(str) [2]
        # Object - list-of-ObjectProperty + Term(3 Bytes) [3]
        # StrictArray - 4 Bytes + len(value) * ValueSize

        adding_data = {
            'duration': 0.0,    # (2B + 8 char) + 1[type] + 8[double] = 19 Bytes
            'filesize': 0.0,    # (2B + 8 char) + 1[type] + 8[double] = 19 Bytes
            'keyframes':        # (2B + 9 char) + 1[type] + (list-excluded) + 3[Term] = 15 Bytes
                {'filepositions':  # (2B + 13 char) + 1[type] + (list-excluded) = 16 Bytes
                     [1402.0, ],  # StrictArray[double] 4B + 8 * len
                'times': [0.0, ]}  # (2B + 5 char) + 1[type] + (4B + 8 * len)
            # 15 + 16 + 4 + 8 * 41 + 2 + 5 + 1 + 4 + 8 * 41 = 703  X
        }

        # todo: calculate the correct bytes needed by the new data



        # add to onMetaData

        # fix file position and timestamp
        # DO NOT change the original tags !!!



    def find_key_frames(self) -> List[FlvTag]:
        """
        For live stream flv, the timestamp data is not the offset for this file.
        We fix the value to correct one, while encode all key frame information.
        """
        keyframes = []

        for tag in self.body:
            if isinstance(tag, FlvTag):
                if tag.tag_type == TagType.Video:
                    if tag.video_tag_header.frame_type == FrameType.KeyFrame:
                        keyframes.append(tag)

        return keyframes


