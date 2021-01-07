from ubxlib.cid import UbxCID
from ubxlib.parser_ubx import UbxParser


class TestParserUbx:
    FRAME_1 = [
        0xB5, 0x62, 0x13, 0x40, 0x18, 0x00, 0x10, 0x00, 0x00, 0x12, 0xE4, 0x07, 0x09, 0x05, 0x06,
        0x28, 0x30, 0x00, 0x40, 0x28, 0xEF, 0x0C, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x51, 0xAC,
    ]

    def test_no_frames(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        packet = uut.packet()
        assert packet == (None, None)

    def test_process(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x13, 0x40))
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid == UbxCID(0x13, 0x40)

    def test_passes_filter(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x13, 0x40))
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid == UbxCID(0x13, 0x40)

    def test_dropped_cls(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x12, 0x40))
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid is None and packet is None

    def test_dropped_id(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x13, 0x41))
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid is None and packet is None

    def test_multiple_filters(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        cids = [UbxCID(0x12, 0x12),
                UbxCID(0x13, 0x40),
                UbxCID(0xFF, 0x00),
                UbxCID(0xFF, 0x00)]
        uut.set_filters(cids)
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid == UbxCID(0x13, 0x40)

    def test_change_filter(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x13, 0x40))
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid == UbxCID(0x13, 0x40)

        uut.set_filter(UbxCID(0x00, 0x00))
        uut.process(self.FRAME_1)
        cid, packet = uut.packet()
        assert cid is None and packet is None

    def test_crc_error(self):
        # B5 62 13 40 18 00 10 00 00 12 E4 07 09 05 06 28 30 00 40 28 EF 0C 0A 00 00 00 00 00 00 00 51 AC
        # hdr  | <--                                 checksum                                  --> | chksum
        frame = [
            0xB5, 0x62, 0x13, 0x40, 0x18, 0x00, 0x10, 0x00, 0x00, 0x12, 0xE4, 0x07, 0x09, 0x05,
            0x06, 0x28, 0x30, 0x00, 0x40, 0x28, 0xEF, 0x0C, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x51, 0xAC + 1
        ]
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x13, 0x41))
        uut.process(frame)      # CRC packet
        cid, packet = uut.packet()
        assert cid == UbxCID(0x00, 0x02)

    def test_cinvalid_length(self):
        frame = [
            0xB5, 0x62, 0x13, 0x40, 0xe9, 0x03, 0x10, 0x00, 0x00, 0x12, 0xE4, 0x07, 0x09, 0x05,
            0x06, 0x28, 0x30, 0x00, 0x40, 0x28, 0xEF, 0x0C, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x51, 0xAC
        ]
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filter(UbxCID(0x13, 0x41))
        uut.process(frame)      # CRC packet
        cid, packet = uut.packet()  # Should be None because frame is too long (MAX_MESSAGE_LENGTH)
        assert cid is None and packet is None

    def test_filters(self):
        uut = UbxParser(UbxCID(0x00, 0x02))
        uut.set_filters([UbxCID(0x05, 0x00), UbxCID(0x05, 0x01)])
        assert len(uut.wait_cids) == 2
        assert UbxCID(0x05, 0x00) in uut.wait_cids
        assert UbxCID(0x05, 0x01) in uut.wait_cids
