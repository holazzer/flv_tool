from struct import unpack, pack
from typing import BinaryIO, Optional


class BaseWriter:
    def __init__(self):
        self.f: Optional[BinaryIO] = None

    def write_UI8(self, i: int) -> int:
        ui8 = pack(">B", i)
        return self.f.write(ui8)

    def write_SI8(self, i: int) -> int:
        si8 = pack(">b", i)
        return self.f.write(si8)

    def write_byte(self, b: bytes) -> int:
        return self.f.write(b)

    def write_UI32(self, i: int) -> int:
        ui32 = pack(">I", i)
        return self.f.write(ui32)

    def write_double(self, v) -> int:
        double = pack(">d", v)
        return self.f.write(double)

    def write_UI16(self, i: int) -> int:
        ui16 = pack(">H", i)
        return self.f.write(ui16)

    def write_SI16(self, i: int) -> int:
        si16 = pack(">h", i)
        return self.f.write(si16)

    def write_string_no_term(self, s: str) -> int:
        return self.f.write(s.encode(encoding='utf-8'))

    def write_UI24(self, i: int) -> int:
        # unsigned 24 bit integer
        ui32 = pack(">I", i)
        b1, b2, b3, b4 = ui32
        ui24 = pack("3B", b2, b3, b4)
        return self.f.write(ui24)

    def write_SI24(self, i: int) -> int:
        # signed 24 bit integer
        si32 = pack(">I", i)
        b1, b2, b3, b4 = si32
        b = b1 & 0b10000000     # sign
        b |= (b2 & 0b01111111)  # high 7 bits
        si24 = pack("3B", b, b3, b4)
        return self.f.write(si24)


