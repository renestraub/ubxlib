import pytest

from ubxlib.types import CfgKeyData


class TestCfgKey:
    CFG_SFIMU_IMU_MNTALG_YAW = 0x4006002d

    def test_basic_unpack(self):
        u = CfgKeyData('test2')
        assert u.name == 'test2'
        assert u.value == None

        consumed = u.unpack(bytearray.fromhex('2D 00 06 40 11 22 33 44'))
        assert consumed == 8
        assert u.bits == 32
        assert u.group_id == 0x06
        assert u.item_id == 0x02D
        assert u.value == 0x44332211

    def test_basic_ids(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('FF 03 FF 40 11 22 33 44'))
        assert consumed == 8
        assert u.bits == 32
        assert u.group_id == 0xFF
        assert u.item_id == 0x3FF

    def test_no_header_data(self):
        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # No data at all
            u.unpack(bytearray.fromhex(''))

        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # Just one byte instead of four
            u.unpack(bytearray.fromhex('FF'))

        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # three bytes instead of four
            u.unpack(bytearray.fromhex('FF FF FF'))

    def test_invalid_length(self):
        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # -----------------------------------v Invalid length field (0)
            u.unpack(bytearray.fromhex('11 01 22 00 11 22 33 44'))

        with pytest.raises(ValueError):
            # -----------------------------------v Invalid length field (6)
            u.unpack(bytearray.fromhex('11 01 22 60 11 22 33 44'))

        with pytest.raises(ValueError):
            # -----------------------------------v Invalid length field (7)
            u.unpack(bytearray.fromhex('11 01 22 70 11 22 33 44'))

    def test_bit(self):
        u = CfgKeyData('test')
        u.unpack(bytearray.fromhex('00 00 00 10 00'))
        assert u.bits == 1
        assert u.value == False

        u = CfgKeyData('test2')
        u.unpack(bytearray.fromhex('00 00 00 10 01'))
        assert u.bits == 1
        assert u.value == True

    def test_bit_invalid_data(self):
        with pytest.raises(ValueError):
            u = CfgKeyData('test')
            u.unpack(bytearray.fromhex('00 00 00 10 FF'))

    def test_u8(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('00 00 00 20 11'))
        assert consumed == 5
        assert u.bits == 8
        assert u.value == 0x11

        u = CfgKeyData('test00')
        u.unpack(bytearray.fromhex('00 00 00 20 00'))
        assert u.value == 0x00

        u = CfgKeyData('testFF')
        u.unpack(bytearray.fromhex('00 00 00 20 FF'))
        assert u.value == 0xFF

    def test_u16(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('00 00 00 30 11 22'))
        assert consumed == 6
        assert u.bits == 16
        assert u.value == 0x2211

        u = CfgKeyData('test0000')
        u.unpack(bytearray.fromhex('00 00 00 30 00 00'))
        assert u.value == 0x0000

        u = CfgKeyData('testFFFF')
        u.unpack(bytearray.fromhex('00 00 00 30 FF FF'))
        assert u.value == 0xFFFF

    def test_u32(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('00 00 00 40 11 22 33 44'))
        assert consumed == 8
        assert u.bits == 32
        assert u.value == 0x44332211

        u = CfgKeyData('test0')
        u.unpack(bytearray.fromhex('00 00 00 40 00 00 00 00'))
        assert u.value == 0x00000000

        u = CfgKeyData('testAllF')
        u.unpack(bytearray.fromhex('00 00 00 40 FF FF FF FF'))
        assert u.value == 0xFFFFFFFF

    def test_u64(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('00 00 00 50 11 22 33 44 55 66 77 88'))
        assert consumed == 12
        assert u.bits == 64
        assert u.value == 0x8877665544332211

    def test_too_few_data(self):
        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # One byte missing for u32
            u.unpack(bytearray.fromhex('00 00 00 40 11 22 33'))

        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # No data at all
            u.unpack(bytearray.fromhex('00 00 00 40'))
