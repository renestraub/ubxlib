import pytest

from ubxlib.frame_factory import FrameFactory
from ubxlib.frame import UbxCID
from ubxlib.ubx_ack import UbxAckAck
from ubxlib.ubx_mon_ver import UbxMonVer


@pytest.fixture(scope="function")
def frame_factory():
    print("setup frame_factory")
    ff = FrameFactory.getInstance()
    yield ff  # provide the fixture value

    print("teardown frame_factory")
    # Next run needs a fresh factory object -> destroy singleton
    FrameFactory.destroy()

class TestFactory:
    def test_singleton(self):
        ff1 = FrameFactory.getInstance()
        ff2 = FrameFactory.getInstance()
        assert id(ff1) == id(ff2)

    def test_registration(self, frame_factory):
        frame_factory.register(UbxAckAck)
        f1 = frame_factory.build(UbxCID(5, 1))
        assert type(f1) == UbxAckAck

    def test_unkown_frame(self, frame_factory):
        frame_factory.register(UbxAckAck)

        with pytest.raises(KeyError):
            m = frame_factory.build(UbxCID(99, 99))

    def test_multiple_registrations(self, frame_factory):
        frame_factory.register(UbxAckAck)
        frame_factory.register(UbxMonVer)

        f1 = frame_factory.build(UbxAckAck.CID)
        assert type(f1) == UbxAckAck

        f2 = frame_factory.build(UbxMonVer.CID)
        assert type(f2) == UbxMonVer

    def test_frame_construct(self, frame_factory):
        frame_factory.register(UbxAckAck)

        data = bytearray.fromhex('11 22')
        f = frame_factory.build_with_data(UbxAckAck.CID, data)
        assert f.CID == UbxCID(0x05, 0x01)
        assert f.f.clsId == 0x11
        assert f.f.msgId == 0x22

    def test_construct_unkown_frame(self, frame_factory):
        with pytest.raises(KeyError):
            data = bytearray.fromhex('11 22')
            frame_factory.build_with_data(UbxAckAck.CID, data)

    def test_only_prototype_classes_can_be_registered(self, frame_factory):
        ack = UbxAckAck()
        with pytest.raises(Exception):
            frame_factory.register(ack)

    def test_throws_when_unknown_frame_shall_be_built(self, frame_factory):
        unregistered_cid = UbxCID(0xCA, 0xFE)
        with pytest.raises(KeyError):
            frame_factory.build(unregistered_cid)

        with pytest.raises(KeyError):
            frame_factory.build_with_data(unregistered_cid, "12345")
