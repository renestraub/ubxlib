from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Fields, X2, X4, U2, U4


class UbxEsfMeas_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_ESF, 0x02)
    NAME = 'UBX-ESF-MEAS'


class UbxEsfMeas(UbxEsfMeas_):
    def __init__(self):
        super().__init__()

        self.f = Fields()
        self.f.add(U4('timeTag'))
        self.f.add(X2('flags'))
        self.f.add(U2('id'))
        self.f.add(X4('data'))
