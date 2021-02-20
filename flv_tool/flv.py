"""
Flv Tool, early impl

* Do not handle encryption! (yet)
 (Do people still use that? After all, Adobe successfully killed Flash.)
 ( Will Adobe please release the source code for flash, since you paid
     big price on it and threw it like trash (what's wrong with u)? )
"""

from typing import List

from flv_tool.flv_tags import BaseFlvTag, FlvHeader


class FLV:
    def __init__(self):
        self.name: str = None
        self.header: FlvHeader = FlvHeader()
        self.body: List[BaseFlvTag] = []


