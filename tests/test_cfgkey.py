import pytest

from ubxlib.cfgkeys import CfgKeyData, UbxKeyId


class TestCfgKeyUnpack:
    def test_basic_unpack(self):
        u = CfgKeyData('test2')
        assert u.name == 'test2'
        assert u.value is None

        consumed = u.unpack(bytearray.fromhex('2D 00 06 40 11 22 33 44'))
        assert consumed == 8
        assert u.bits == 32
        assert u.signed is False
        assert u.group_id == 0x06
        assert u.item_id == 0x02D
        assert u.value == 0x44332211

    def test_basic_ids(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('FF 03 FF 40 11 22 33 44'))
        assert consumed == 8
        assert u.bits == 32
        assert u.signed is False
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
        assert u.signed is False
        assert u.value is False

        u = CfgKeyData('test2')
        u.unpack(bytearray.fromhex('00 00 00 10 01'))
        assert u.bits == 1
        assert u.signed is False
        assert u.value is True

    def test_bit_invalid_data(self):
        with pytest.raises(ValueError):
            u = CfgKeyData('test')
            u.unpack(bytearray.fromhex('00 00 00 10 FF'))

    def test_u8(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('00 00 00 20 11'))
        assert consumed == 5
        assert u.bits == 8
        assert u.signed is False
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
        assert u.signed is False
        assert u.value == 0x2211

        u = CfgKeyData('test0000')
        u.unpack(bytearray.fromhex('00 00 00 30 00 00'))
        assert u.value == 0x0000

        u = CfgKeyData('testFFFF')
        u.unpack(bytearray.fromhex('00 00 00 30 FF FF'))
        assert u.value == 0xFFFF

    def test_i16(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('2e 00 06 30 00 80'))
        assert consumed == 6
        assert u.bits == 16
        assert u.signed is True
        assert u.value == -32768

    def test_u32(self):
        u = CfgKeyData('test')
        consumed = u.unpack(bytearray.fromhex('00 00 00 40 11 22 33 44'))
        assert consumed == 8
        assert u.bits == 32
        assert u.signed is False
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


class TestCfgKeyCreation:
    def test1(self):
        u = CfgKeyData.from_key(UbxKeyId.CFG_RATE_MEAS, 250)
        assert u.bits == 16
        assert u.signed is False
        assert u.value == 250
        assert u.group_id == 0x21
        assert u.item_id == 0x001
        assert str(u) == '<anon>: key: CFG-RATE_MEAS, bits: 16, value: 250 (0x00fa)'

    def test2(self):
        u = CfgKeyData.from_key(UbxKeyId.CFG_SIGNAL_GPS_ENA, True)
        assert u.bits == 1
        assert u.signed is False
        assert u.value is True
        assert u.group_id == 0x31
        assert u.item_id == 0x01f
        assert str(u) == '<anon>: key: CFG-SIGNAL-GPS_ENA, bits: 1, value: True'

    def test3(self):
        u = CfgKeyData.from_key(UbxKeyId.CFG_SFIMU_IMU_MNTALG_YAW, 12345)
        assert u.bits == 32
        assert u.signed is False
        assert u.value == 12345
        assert u.group_id == 0x06
        assert u.item_id == 0x02d
        assert str(u) == '<anon>: key: CFG-SFIMU-IMU_MNTALG_YAW, bits: 32, value: 12345 (0x00003039)'

    def test4(self):
        u = CfgKeyData.from_key(UbxKeyId.CFG_SFIMU_IMU_MNTALG_PITCH, -100)
        assert u.bits == 16
        assert u.signed is True
        assert u.value == -100
        assert u.group_id == 0x06
        assert u.item_id == 0x02e
        assert str(u) == '<anon>: key: CFG-SFIMU-IMU_MNTALG_PITCH, bits: 16, value: -100'

        u = CfgKeyData.from_key(UbxKeyId.CFG_SFIMU_IMU_MNTALG_ROLL, -12345)
        assert u.bits == 16
        assert u.signed is True
        assert u.value == -12345
        assert u.group_id == 0x06
        assert u.item_id == 0x02f
        assert str(u) == '<anon>: key: CFG-SFIMU-IMU_MNTALG_ROLL, bits: 16, value: -12345'


class TestCfgKeyPack:
    def test_u64(self):
        u = CfgKeyData('test0', 0x06, 0x2d, 64, 0x8877665544332211)
        data = u.pack()
        assert data == bytearray.fromhex('2D 00 06 50 11 22 33 44 55 66 77 88')

    def test_u32(self):
        u = CfgKeyData('test1', 0x06, 0x2d, 32, 0x44332211)
        data = u.pack()
        assert data == bytearray.fromhex('2D 00 06 40 11 22 33 44')

    def test_i32(self):
        u = CfgKeyData('test1', 0x06, 0x2d, 32, -12345678, True)
        data = u.pack()
        assert data == bytearray.fromhex('2D 00 06 40 b2 9e 43 ff')

    def test_u16(self):
        u = CfgKeyData('test2', 0x12, 0x145, 16, 0x7788)
        data = u.pack()
        assert data == bytearray.fromhex('45 01 12 30 88 77')

    def test_i16(self):
        u = CfgKeyData('test2', 0x12, 0x145, 16, -32768, True)
        data = u.pack()
        assert data == bytearray.fromhex('45 01 12 30 00 80')

    def test_u8(self):
        u = CfgKeyData('test2', 0x06, 0x2d, 8, 0x55)
        data = u.pack()
        assert data == bytearray.fromhex('2D 00 06 20 55')

    def test_bool(self):
        u = CfgKeyData('test2', 0x06, 0x2d, 1, True)
        data = u.pack()
        assert data == bytearray.fromhex('2D 00 06 10 01')

        u = CfgKeyData('test1', 0x06, 0x2d, 1, False)
        data = u.pack()
        assert data == bytearray.fromhex('2D 00 06 10 00')

    def test_basic_ids(self):
        u = CfgKeyData('test3', 0x00, 0x000, 8, 0x66)
        data = u.pack()
        assert data == bytearray.fromhex('00 00 00 20 66')

        u = CfgKeyData('test4', 0xFF, 0x3FF, 8, 0x55)
        data = u.pack()
        assert data == bytearray.fromhex('FF 03 FF 20 55')

    def test_value_too_large(self):
        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            u = CfgKeyData('test4', 0xFF, 0x3FF, 16, 0xFFFF+1)
            _ = u.pack()

        u = CfgKeyData('test')
        with pytest.raises(ValueError):
            # No data at all
            u.unpack(bytearray.fromhex('00 00 00 40'))

    def test_invalid_ids(self):
        with pytest.raises(ValueError):
            u = CfgKeyData('test', -1, 0, 16, 0x1234)
            _ = u.pack()

        with pytest.raises(ValueError):
            u = CfgKeyData('test', 0x100, 0, 16, 0x1234)
            _ = u.pack()

        with pytest.raises(ValueError):
            u = CfgKeyData('test', 0, -1, 16, 0x1234)
            _ = u.pack()

        with pytest.raises(ValueError):
            u = CfgKeyData('test', 0, 0x1000, 16, 0x1234)
            _ = u.pack()
