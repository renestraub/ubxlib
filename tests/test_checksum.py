import pytest

from ubxlib.checksum import Checksum


class TestChecksum:
    def test_creation(self):
        dut = Checksum()
        assert dut.matches(0x00, 0x00)

    def test_reset(self):
        dut = Checksum()
        dut.add(0xF0)
        dut.add(0xE0)

        dut.reset()
        assert dut.matches(0x00, 0x00)

    def test_calculation(self):
        # B5 62 13 40 18 00 10 00 00 12 E4 07 09 05 06 28 30 00 40 28 EF 0C 0A 00 00 00 00 00 00 00 51 AC
        # hdr  | <--                                 checksum                                  --> | chksum

        dut = Checksum()
        frame = [
            0x13, 0x40, 0x18, 0x00, 0x10, 0x00, 0x00, 0x12, 0xE4, 0x07, 0x09, 0x05, 0x06, 0x28,
            0x30, 0x00, 0x40, 0x28, 0xEF, 0x0C, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        ]
        for byte in frame:
            dut.add(byte)

        assert dut.matches(0x51, 0xAC)
