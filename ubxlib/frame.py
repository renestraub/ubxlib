import struct

from ubxlib.checksum import Checksum
from ubxlib.cid import UbxCID
from ubxlib.types import Fields


# TODO: Flag/State that shows whether frame is fully constructed and can be sent to module
# TODO: True for Action Frames, which are typically small and have only a selector value
# TODO: True for frames that have been constructed from a poll request
class UbxFrame(object):
    CID = UbxCID(0, 0)
    NAME = 'UBX'

    SYNC_1 = 0xb5
    SYNC_2 = 0x62

    @classmethod
    def construct(cls, data):
        obj = cls()
        obj.data = data
        obj.unpack()
        return obj

    @classmethod
    def MATCHES(cls, cid):
        return cls.CID == cid

    def __init__(self):
        super().__init__()
        self.data = bytearray()
        # TODO: Do we need checksum as member?
        self.checksum = Checksum()
        self.f = Fields()

    def to_bytes(self):
        self._calc_checksum()

        msg = bytearray([UbxFrame.SYNC_1, UbxFrame.SYNC_2])
        msg.append(self.CID.cls)
        msg.append(self.CID.id)

        length = len(self.data)
        msg.append((length >> 0) % 0xFF)
        msg.append((length >> 8) % 0xFF)

        msg += self.data
        msg.append(self.cka)
        msg.append(self.ckb)

        return msg

    def get(self, name):
        return self.f.get(name)

    def pack(self):
        self.data = self.f.pack()

    def unpack(self):
        self.f.unpack(self.data)

    def _calc_checksum(self):
        self.checksum.reset()

        self.checksum.add(self.CID.cls)
        self.checksum.add(self.CID.id)

        length = len(self.data)
        self.checksum.add((length >> 0) & 0xFF)
        self.checksum.add((length >> 8) & 0xFF)

        for d in self.data:
            self.checksum.add(d)

        self.cka, self.ckb = self.checksum.value()

    def __str__(self):
        res = f'{self.NAME} {self.CID}'
        res += str(self.f)
        return res
