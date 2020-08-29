from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import U1


class UbxUpdSos_(UbxFrame):
    NAME = 'UBX-UPD-SOS'
    CID = UbxCID(0x09, 0x14)


class UbxUpdSosPoll(UbxUpdSos_):
    NAME = UbxUpdSos_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxUpdSos(UbxUpdSos_):

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


class UbxUpdSosAction(UbxUpdSos_):
    NAME = UbxUpdSos_.NAME + '-ACTION'

    SAVE = 0
    CLEAR = 1

    def __init__(self):
        super().__init__()

        self.f.add(U1('cmd'))
        self.f.add(U1('res1_1'))
        self.f.add(U1('res1_2'))
        self.f.add(U1('res1_3'))
