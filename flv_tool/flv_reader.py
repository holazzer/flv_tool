from struct import unpack

from flv_tool.base_reader import BaseReader
from flv_tool.flv import FLV
from flv_tool.flv_tags import PrevTagSize, FlvTag, AudioTagHeader, VideoTagHeader, BinaryData, ScriptDataValue, \
    ScriptDataDate, ScriptDataECMAArray, ScriptDataLongString, ScriptDataObject, ScriptDataObjectProperty, \
    ScriptDataStrictArray, ScriptDataString, ScriptData
from flv_tool.flv_enums import TagType, SoundFormat, SoundRate, SoundSize, SoundType, AACPacketType, FrameType, CodecID, \
    AVCPacketType, ValueType


class FlvReader(BaseReader):
    def __init__(self, f):
        super(FlvReader, self).__init__(f)
        self.flv: FLV = None
        self.file_length = self.f.seek(0, 2)
        self.f.seek(0)

    def read_flv(self) -> FLV:
        self.flv = FLV()
        self.flv.f = self.f
        self.flv.reader = self
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



