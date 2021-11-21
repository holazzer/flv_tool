from flv_tool.flv_tags import BaseFlvTag, FlvHeader, FlvTag, ScriptData,\
    ScriptDataString, ScriptDataStrictArray, ScriptDataObjectProperty,\
    ScriptDataObject, ScriptDataLongString, ScriptDataECMAArray, \
    ScriptDataDate, ScriptDataValue

from flv_tool.flv_enums import TagType, ValueType
from flv_tool.flv import FLV
from flv_tool.base_writer import BaseWriter

from typing import List, Dict, Union, Any, BinaryIO, Optional
import copy


class FlvBuilder(BaseWriter):
    def __init__(self, flv: FLV):
        super().__init__()
        self.original_flv: FLV = flv
        self.build: FLV = copy.deepcopy(flv)
        self.logs: List[str] = []

    def fix_meta(self):
        """
        Check if the onMetaData Script Tag misses any fields and fix them.
        This is useful when you save streaming flv data to disk.
        The streaming flv data lacks certain fields,
        which although still good for sequential streaming,
        but for most video player software, they don't
        have correct video duration or random access.

        check list:
            + fileSize
            + duration
            + keyframes

        This method will first check if the field exists,
            and then fix it or add it if it doesn't.

        This will only effect the property `build`.
        The original flv object and original video file will not change.
        """

        pass

    def write_build_to_file(self, path: str):
        pass


