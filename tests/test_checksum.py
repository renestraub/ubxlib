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

    def test_calculation_crc_error1(self):
        # Frame with CRC error
        #          **
        # B5 62 01 00 14 00 54 a0 06 0f 00 00 00 00 00 00 00 00 01 00 00 00 03 00 00 00 33 46
        # hdr  | <--                          checksum                             --> | chksum

        # No frame 0x01 0x00 found
        # 0x11 missing as ID could explain checksum difference 22bf vs 3346. Check with test
        dut = Checksum()
        frame = [
            0x01, 0x00, 0x14, 0x00, 0x54, 0xa0, 0x06, 0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00
        ]
        for byte in frame:
            dut.add(byte)

        assert dut.matches(0x22, 0xBF)      # Checksum for incorrect frame

        # Fix faulty byte at position 1: Wrong 0x00, correct 0x11
        dut.reset()
        frame[1] = 0x11
        for byte in frame:
            dut.add(byte)

        # print(f'{dut._cka:02x} {dut._ckb:02x}')
        assert dut.matches(0x33, 0x46)

    def test_calculation_crc_error2(self):
        # Frame with CRC error
        #                                                                **
        # B5 62 01 11 14 00 50 2b d7 11 01 00 00 00 00 00 00 00 01 00 00 4c 03 00 00 00 8e 2b
        # hdr  | <--                          checksum                             --> | chksum

        # Frame looks ok, except ecefVZ, guess 4c should be 00
        dut = Checksum()
        frame = [
            0x01, 0x11, 0x14, 0x00, 0x50, 0x2b, 0xd7, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x01, 0x00, 0x00, 0x4c, 0x03, 0x00, 0x00, 0x00
        ]
        for byte in frame:
            dut.add(byte)

        assert dut.matches(0xda, 0xa7)      # Checksum for incorrect frame

        # Fix faulty byte at position 19: Wrong 0x4C, correct 0x00
        dut.reset()
        frame[19] = 0x00
        for byte in frame:
            dut.add(byte)

        print(f'{dut._cka:02x} {dut._ckb:02x}')
        assert dut.matches(0x8e, 0x2b)

    def test_calculation_crc_error3(self):
        # Frame with CRC error
        #
        # B5 62 01 01 14 00 54 a0 06 ff 02 4e 92 19 0f f6 94 03 a5 2c d0 1b 44 00 00 00 b6 b1
        # hdr  | <--                          checksum                             --> | chksum

        # iTOW of next messages is 54 a0 06 0f instead of .. .. .. ff
        dut = Checksum()
        frame = [
            0x01, 0x01, 0x14, 0x00, 0x54, 0xa0, 0x06, 0xff, 0x02, 0x4e, 0x92, 0x19, 0x0f, 0xf6,
            0x94, 0x03, 0xa5, 0x2c, 0xd0, 0x1b, 0x44, 0x00, 0x00, 0x00
        ]
        for byte in frame:
            dut.add(byte)

        assert dut.matches(0xa6, 0xa1)      # Checksum for incorrect frame

        # Fix faulty byte at position 19: Wrong 0x4C, correct 0x00
        dut.reset()
        frame[7] = 0x0F
        for byte in frame:
            dut.add(byte)

        # print(f'{dut._cka:02x} {dut._ckb:02x}')
        assert dut.matches(0xb6, 0xb1)
