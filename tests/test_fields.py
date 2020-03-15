# import pytest

from ubxlib.types import Fields
from ubxlib.types import U1, I4


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
