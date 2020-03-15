# import pytest

from ubxlib.frame import UbxCID

class TestCID:
    def test_creation(self):
        c = UbxCID(0x05, 0x01)
        assert c.cls == 0x05
        assert c.id == 0x01

    def test_print(self):
        c = UbxCID(0x05, 0x01)
        res = str(c)
        print(res)
        assert res == 'cls:05 id:01'

    def test_equal(self):
        c1 = UbxCID(0x05, 0x01)
        c2 = UbxCID(0x05, 0x01)
        assert c1 == c2

    def test_not_equal(self):
        c1 = UbxCID(0x05, 0x00)
        c2 = UbxCID(0x05, 0x01)
        assert c1 != c2

        c1 = UbxCID(0x05, 0x01)
        c2 = UbxCID(0x06, 0x01)
        assert c1 != c2
