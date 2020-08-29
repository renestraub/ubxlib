import pytest

from ubxlib.cid import UbxCID


class TestCID:
    def test_creation(self):
        c = UbxCID(0x05, 0x01)
        assert c.cls == 0x05
        assert c.id == 0x01

    def test_print(self):
        c = UbxCID(0x05, 0x01)
        res = str(c)
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

    def test_immutable(self):
        c1 = UbxCID(0x05, 0x01)
        with pytest.raises(AttributeError):
            c1.cls = 0x06

        with pytest.raises(AttributeError):
            c1.id = 0x44

        res = str(c1)
        assert res == 'cls:05 id:01'
