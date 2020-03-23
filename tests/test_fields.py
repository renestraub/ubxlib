# import pytest

from ubxlib.types import Fields
from ubxlib.types import Padding, U1, I4


class TestFields:
    def test_creation(self):
        u = Fields()
        u.add(U1('cmd'))

    def test_set_field1(self):
        u = Fields()
        u.add(U1('cmd'))
        u.cmd = 1

        assert u._fields['cmd'].value == 1

    def test_set_field2(self):
        u = Fields()
        u.add(U1('cmd'))
        u.add(U1('val'))
        u.cmd = 1
        u.val = 3

        assert u._fields['cmd'].value == 1
        assert u._fields['val'].value == 3

    def test_set_field3(self):
        u = Fields()
        u.add(I4('test'))
        u.add(U1('val'))
        u.test = 0x12345678
        u.val = 0xFF

        assert u._fields['test'].value == 0x12345678
        assert u._fields['val'].value == 0xFF
        assert u.test == 0x12345678
        assert u.val == 0xFF

    # test_set_field_out_of_range(self):

    def test_pack1(self):
        u = Fields()
        u.add(I4('test'))
        u.add(U1('val'))
        u.add(Padding(3, 'res1'))
        u.add(I4('test2'))

        u.test = 0x98765432
        u.val = 0xAF
        u.test2 = 0xcafebabe

        data = u.pack()
        print(data)
        assert data == bytearray.fromhex('32 54 76 98 AF 00 00 00 be ba fe ca')

    def test_pack2(self):
        u = Fields()
        u.add(I4('test'))
        u.add(U1('val'))
        u.add(Padding(2, 'res1'))

        u.test = 0x98765432
        u.val = 0xAF
        u.test2 = 0xcafebabe

        data = u.pack()
        assert data == bytearray.fromhex('32 54 76 98 AF 00 00')

    def test_unpack(self):
        # single U8
        # single integer
        # combined message
        # string
        pass
