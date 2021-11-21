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







