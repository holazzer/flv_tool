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
    BinaryData, \
    ScriptDataValue, \
    ScriptDataDate, \
    ScriptDataECMAArray, \
    ScriptDataLongString, \
    ScriptDataObject, \
    ScriptDataObjectProperty, \
    ScriptDataStrictArray, \
    ScriptDataString, \
    ScriptData

from flv_tool.flv_enums import TagType, FrameType, ValueType
from flv_tool.flv_writer import FlvWriter


class FLV:
    def __init__(self):
        self.name: str = None
        self.header: FlvHeader = FlvHeader()
        self.body: List[BaseFlvTag] = []
        self.f: BytesIO = None
        self.reader: 'FlvReader' = None

    def fix_stream_flv(self):
        keyframes = self.find_key_frames()

        # note: we only need the number of keyframes to
        # determine extra bytes needed

        # calculate offset
        len_kf = len(keyframes)

        on_meta_data: ScriptData = self.body[1].data
        arr: ScriptDataECMAArray = on_meta_data.value.script_data_value

        # onMetaData is an `ECMA_array`,
        # where each item is a `ObjectProperty`
        # name is a 'DataString' len = 2 Bytes (str len) + len(str)
        # value is a 'DataValue' len =
        # double - 8 Bytes [0]
        # Boolean - 1 Byte (UI8) [1]
        # String - len(str) [2]
        # Object - list-of-ObjectProperty + Term(3 Bytes) [3]
        # StrictArray - 4 Bytes + len(value) * ValueSize


        # todo: calculate these

        filesize = self.reader.file_length
        file_positions = [i.first_byte_after for i in keyframes]
        original_times = [i.real_timestamp for i in keyframes]
        starting_time = original_times[1]
        times = [(i-starting_time if i > 0 else i)/1000 for i in original_times]

        # find last video tag
        last_video_tag = None
        for tag in reversed(self.body):
            if isinstance(tag, FlvTag) and tag.tag_type == TagType.Video:
                last_video_tag = tag
                break
        assert last_video_tag is not None

        duration = (last_video_tag.real_timestamp - starting_time) / 1000

        #adding_data = {
        #    'duration': 0.0,  # (2B + 8 char) + 1[type] + 8[double] = 19 Bytes
        #    'filesize': 0.0,  # (2B + 8 char) + 1[type] + 8[double] = 19 Bytes
        #    'keyframes':  # (2B + 9 char) + 1[type] + (list-excluded) + 3[Term] = 15 Bytes
        #        {'filepositions':  # (2B + 13 char) + 1[type] + (list-excluded) = 16 Bytes
        #             [1402.0, ],  # StrictArray[double] 4B + (8+1) * len
        #         'times': [0.0, ]}  # (2B + 5 char) + 1[type] + (4B + 8 * len)
        #    # keyframes 785 =
        #}

        # todo: calculate the correct bytes needed by the new data

        offset = 0

        # this encoder info ^v^
        fixer = ScriptDataObjectProperty()

        fixer.property_name = ScriptDataString()
        fixer.property_name.string_data = "meta_fixer"  # 10
        offset += len(fixer.property_name.string_data)

        fixer.property_name.string_length = len(fixer.property_name.string_data)  # 2
        offset += 2

        fixer.property_data = ScriptDataValue()
        fixer.property_data.type = ValueType.String  # 1
        offset += 1

        fixer.property_data.script_data_value = ScriptDataString()
        fixer.property_data.script_data_value.string_data = "flv_tool by @holazzer"  # 21
        offset += len(fixer.property_data.script_data_value.string_data)

        fixer.property_data.script_data_value.string_length = len(
            fixer.property_data.script_data_value.string_data)  # 2
        offset += 2

        arr.variables.append(fixer)

        # duration

        if 'duration' not in on_meta_data.value.py_native_value:
            dur = ScriptDataObjectProperty()

            dur.property_name = ScriptDataString()
            dur.property_name.string_data = "duration"
            offset += len(dur.property_name.string_data)
            dur.property_name.string_length = len(dur.property_name.string_data)
            offset += 2

            dur.property_data = ScriptDataValue()
            dur.property_data.type = ValueType.Number
            offset += 1
            dur.property_data.script_data_value = duration  # todo: check duration
            offset += 8

            arr.variables.append(dur)

        else:
            dur = None
            for item in arr.variables:
                if item.property_name.string_data == 'duration': dur = item
            assert dur is not None
            assert dur.property_name.string_data == 'duration'
            assert dur.property_data.type == ValueType.Number
            dur.property_data.script_data_value = duration

        if 'filesize' not in on_meta_data.value.py_native_value: offset += 19
        # precompute offset for new filesize

        if 'keyframes' not in on_meta_data.value.py_native_value:
            # keyframes
            kfs = ScriptDataObjectProperty()
            kfs.property_name = ScriptDataString()
            kfs.property_name.string_data = "keyframes"
            kfs.property_name.string_length = len(kfs.property_name.string_data)
            offset += (len(kfs.property_name.string_data) + 2)

            kfs.property_data = ScriptDataValue()
            kfs.property_data.type = ValueType.Object
            offset += 1

            offset += (35 + 2*9*len(file_positions))

            obj = kfs.property_data.script_data_value = ScriptDataObject()

            # file positions
            fp = ScriptDataObjectProperty()
            fp.property_name = ScriptDataString()
            fp.property_name.string_data = "filepositions"
            fp.property_name.string_length = 13
            fp.property_data = ScriptDataValue()
            fp.property_data.type = ValueType.StrictArray
            fp_array = fp.property_data.script_data_value = ScriptDataStrictArray()
            fp_array.strict_array_length = len(file_positions)
            for i in file_positions:
                sa_item = ScriptDataValue()
                sa_item.type = ValueType.Number
                sa_item.script_data_value = i + offset
                fp_array.strict_array_value.append(sa_item)

            obj.object_properties.append(fp)

            # times

            ts = ScriptDataObjectProperty()

            ts.property_name = ScriptDataString()
            ts.property_name.string_data = "times"
            ts.property_name.string_length = 5
            ts.property_data = ScriptDataValue()
            ts.property_data.type = ValueType.StrictArray
            ts_array = ts.property_data.script_data_value = ScriptDataStrictArray()
            ts_array.strict_array_length = len(times)
            for i in times:
                sa_item = ScriptDataValue()
                sa_item.type = ValueType.Number
                sa_item.script_data_value = i
                ts_array.strict_array_value.append(sa_item)

            obj.object_properties.append(ts)

            arr.variables.append(kfs)

        if 'filesize' not in on_meta_data.value.py_native_value:
            size = ScriptDataObjectProperty()
            size.property_name = ScriptDataString()
            size.property_name.string_data = "filesize"
            size.property_name.string_length = len(size.property_name.string_data)
            size.property_data = ScriptDataValue()
            size.property_data.type = ValueType.Number
            size.property_data.script_data_value = filesize + offset
            arr.variables.append(size)

        else:
            size = None
            for item in arr.variables:
                if item.property_name.string_data == 'filesize': size = item
            assert size is not None
            assert size.property_name.string_data == 'filesize'
            assert size.property_data.type == ValueType.Number
            size.property_data.script_data_value = filesize + offset

        prev_tag_size: PrevTagSize = self.body[2]
        prev_tag_size.size += offset

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
