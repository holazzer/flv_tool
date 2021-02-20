from struct import unpack, pack
from typing import BinaryIO


class BaseReader:
    def __init__(self, f):
        self.f: BinaryIO = f

    def read_UI8(self) -> int:
        ui8 = self.f.read(1)
        return unpack("B", ui8)[0]

    def read_SI8(self) -> int:
        ui8 = self.f.read(1)
        return unpack("b", ui8)[0]

    def read_SI24(self) -> int:
        b2, b3, b4 = self.f.read(3)
        b1 = b2 & 0b10000000
        b2 = b2 & 0b01111111
        return unpack('>i', pack('4B', b1, b2, b3, b4))[0]

    def read_byte(self) -> bytes:
        return self.f.read(1)

    def read_UI24(self) -> int:
        b1, b2, b3 = unpack('3B', self.f.read(3))
        return (b1 << 16) + (b2 << 8) + b3

    def read_UI32(self) -> int:
        ui32 = self.f.read(4)
        return unpack(">I", ui32)[0]

    def read_double(self) -> float:
        ui64 = self.f.read(8)
        return unpack(">d", ui64)[0]

    def read_UI16(self) -> int:
        ui16 = self.f.read(2)
        return unpack(">H", ui16)[0]

    def read_SI16(self) -> int:
        ui16 = self.f.read(2)
        return unpack(">h", ui16)[0]

    def read_string_no_term(self, length) -> str:
        s = self.f.read(length)
        return s.decode(encoding='utf-8')