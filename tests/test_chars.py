import pytest

from ubxlib.types import Fields
from ubxlib.types import CH


class TestChars:
    def test_basic_unpack(self):
        u = Fields()
        u.add(CH(4, 'string'))

        u.unpack(bytearray.fromhex('41 42 43 44'))
        assert u.string == 'ABCD'

    def test_basic_pack(self):
        u = Fields()
        u.add(CH(4, 'string'))
        u.string = '1234'

        data = u.pack()
        assert data == bytearray.fromhex("31 32 33 34")

    def test_chars_trailing_zeroes_removed(self):
        u = Fields()
        u.add(CH(10, 'string'))

        u.unpack(bytearray.fromhex('41 42 43 44 45 00 00 00 00 00'))
        assert u.string == 'ABCDE'

    def test_chars_padding_added(self):
        u = Fields()
        u.add(CH(6, 'string'))
        u.string = '1234'

        data = u.pack()
        assert data == bytearray.fromhex('31 32 33 34 00 00')

    def test_chars_too_long(self):
        u = Fields()
        u.add(CH(6, 'string'))
        u.string = '1234567'    # One byte too long

        with pytest.raises(ValueError):
            u.pack()

    def test_chars_invalid_length(self):
        u = Fields()
        u.add(CH(5, 'string'))

        with pytest.raises(ValueError):
            u.unpack(bytearray.fromhex('31 32'))    # Too few bytes

        with pytest.raises(ValueError):
            u.unpack(bytearray.fromhex('31 32 33 34'))    # Too few bytes

    def test_chars_invalid_unicode(self):
        u = Fields()
        u.add(CH(2, 'string'))

        with pytest.raises(ValueError):
            u.unpack(bytearray.fromhex('d8 00'))    # UTF16 reserved code point
