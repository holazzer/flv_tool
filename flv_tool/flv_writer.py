from io import BytesIO

#from flv_tool.flv import FLV

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

from flv_tool.flv_enums import TagType

from flv_tool.base_writer import BaseWriter

from typing import List

from tqdm import tqdm


class FlvWriter(BaseWriter):
    """
    Encode an FLV object into a binary file.
    We assume the FLV object is correct.
    """
    def __init__(self, flv: 'FLV'):
        super().__init__()
        self.flv: 'FLV' = flv
        self.f = BytesIO()

    def write_flv(self):
        self.write_flv_header(self.flv.header)
        self.write_flv_body(self.flv.body)

    def write_flv_header(self, header: FlvHeader):
        self.write_byte(b'FLV')  # signature
        self.write_UI8(header.version)  # version

        flag = 0b00000000
        flag |= (header.flag_audio << 2)
        flag |= (header.flag_video << 0)
        self.write_byte(bytes((flag, )))

        self.write_UI32(header.header_length)

    def write_prev_tag_size(self, prev_tag_size: PrevTagSize):
        self.write_UI32(prev_tag_size.size)

    def write_flv_tag(self, tag: FlvTag):
        b = 0b00000000
        b |= (tag.filter << 5)
        b |= tag.tag_type
        self.write_byte(bytes((b,)))
        self.write_UI24(tag.data_size)
        self.write_UI24(tag.timestamp)
        self.write_UI8(tag.timestamp_extended)
        self.write_UI24(0)  # StreamID

        if tag.tag_type == TagType.Audio:
            self.write_audio_tag_header(tag.audio_tag_header)
        elif tag.tag_type == TagType.Video:
            self.write_video_tag_header(tag.video_tag_header)

        if tag.filter:
            raise NotImplementedError("Encryption Not Implemented")

        if tag.tag_type == TagType.Audio or tag.tag_type == TagType.Video:
            self.write_binary_data(tag.data)
        elif tag.tag_type == TagType.Script:
            self.write_script_data(tag.data)
        else:
            raise ValueError("Invalid TagType: {}".format(tag.tag_type))

    def write_audio_tag_header(self, header: AudioTagHeader):
        return self.copy_data(self.flv.f, header.first_byte_after, header.last_byte_at)

    def write_video_tag_header(self, header: VideoTagHeader):
        return self.copy_data(self.flv.f, header.first_byte_after, header.last_byte_at)

    def write_binary_data(self, data: BinaryData):
        return self.copy_data(self.flv.f, data.first_byte_after, data.last_byte_at)

    def write_script_data_object_end(self):
        self.write_UI8(0)
        self.write_UI8(0)
        self.write_UI8(9)

    def write_script_data_string(self, string: ScriptDataString):
        self.write_UI16(string.string_length)
        self.write_string_no_term(string.string_data)

    def write_script_data_object(self, data_object: ScriptDataObject):
        for item in data_object.object_properties:
            self.write_script_data_object_property(item)
        self.write_script_data_object_end()

    def write_script_data_object_property(self, obj_property: ScriptDataObjectProperty):
        self.write_script_data_string(obj_property.property_name)
        self.write_script_data_value(obj_property.property_data)

    def write_script_data_ecma_array(self, array: ScriptDataECMAArray):
        self.write_UI32(array.array_length)
        for item in array.variables:
            self.write_script_data_object_property(item)
        self.write_script_data_object_end()

    def write_script_data_strict_array(self, array: ScriptDataStrictArray):
        self.write_UI32(array.strict_array_length)
        for item in array.strict_array_value:
            self.write_script_data_value(item)

    def write_script_data_date(self, date: ScriptDataDate):
        self.write_SI16(date.local_date_time_offset)

    def write_script_data_long_string(self, string: ScriptDataLongString):
        self.write_UI32(string.string_length)
        self.write_string_no_term(string.string_data)

    def write_script_data_value(self, value: ScriptDataValue):
        self.write_UI8(value.type)

        if value.type == 0:
            self.write_double(value.script_data_value)
        elif value.type == 1:
            self.write_UI8(value.script_data_value)
        elif value.type == 2:
            self.write_script_data_string(value.script_data_value)
        elif value.type == 3:
            self.write_script_data_object(value.script_data_value)
        elif value.type == 7:
            self.write_UI16(value.script_data_value)
        elif value.type == 8:
            self.write_script_data_ecma_array(value.script_data_value)
        elif value.type == 10:
            self.write_script_data_strict_array(value.script_data_value)
        elif value.type == 11:
            self.write_script_data_date(value.script_data_value)
        elif value.type == 12:
            self.write_script_data_long_string(value.script_data_value)
        else:
            raise ValueError("Undefined ScriptDataValue Type: {}".format(value.type))

    def write_script_data(self, script_data: ScriptData):
        self.write_script_data_value(script_data.name)
        self.write_script_data_value(script_data.value)

    def copy_data(self, f: BytesIO, start: int, stop: int):
        b = bytearray()
        f.seek(start)
        size = stop - start
        while len(b) < size:
            cur = f.tell()
            rr = f.read(stop - cur)
            b.extend(rr)
        return self.write_byte(b)
    # todo: check copy data margin

    def write_flv_body(self, body: List[BaseFlvTag]):
        body = body.copy()
        if not isinstance(body[-1], PrevTagSize): body.pop()
        for tag in tqdm(body):
            if isinstance(tag, PrevTagSize):
                self.write_prev_tag_size(tag)
            elif isinstance(tag, FlvTag):
                self.write_flv_tag(tag)


# todo: implement script data!








