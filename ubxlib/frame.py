import logging
import struct

from ubxlib.checksum import Checksum
from ubxlib.types import U1
from ubxlib.types import Fields

logger = logging.getLogger('gnss_tool')


class UbxCID(object):
    def __init__(self, cls, id):
        super().__init__()
        self.__cls = cls
        self.__id = id

    @property
    def cls(self):
        return self.__cls

    @property
    def id(self):
        return self.__id

    def __eq__(self, other):
        return self.__cls == other.__cls and self.__id == other.__id

    def __str__(self):
        return f'cls:{self.__cls:02x} id:{self.__id:02x}'

    def __hash__(self):
        return hash((self.__cls, self.__id))


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
