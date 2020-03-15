import struct

from ubxlib.frame import UbxFrame, UbxPoll, UbxCID
from ubxlib.types import U1


class UbxUpdSosPoll(UbxPoll):
    CID = UbxCID(0x09, 0x14)
    NAME = 'UBX-CFG-SOS-POLL'

    def __init__(self):
        super().__init__()


class UbxUpdSos(UbxFrame):
    CID = UbxCID(0x09, 0x14)
    NAME = 'UBX-CFG-SOS'

    def __init__(self):
        super().__init__()

        self.f.add(U1('cmd'))
        self.f.add(U1('res1_1'))
        self.f.add(U1('res1_2'))
        self.f.add(U1('res1_3'))
        self.f.add(U1('response'))
        self.f.add(U1('res2_1'))
        self.f.add(U1('res2_2'))
        self.f.add(U1('res2_3'))


class UbxUpdSosAction(UbxFrame):
    CID = UbxCID(0x09, 0x14)
    NAME = 'UBX-CFG-SOS-ACTION'

    def __init__(self):
        super().__init__()

        self.f.add(U1('cmd'))
        self.f.add(U1('res1_1'))
        self.f.add(U1('res1_2'))
        self.f.add(U1('res1_3'))
