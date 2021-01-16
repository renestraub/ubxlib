from .cid import UbxCID
from .frame import UbxFrame
from .types import I1, I4, U1, U2, U4, X2, Padding


class UbxCfgNav5_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x24)
    NAME = 'UBX-CFG-NAV5'


class UbxCfgNav5Poll(UbxCfgNav5_):
    NAME = UbxCfgNav5_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

    def _cls_response(self):
        return UbxCfgNav5


class UbxCfgNav5(UbxCfgNav5_):
    def __init__(self):
        super().__init__()

        self.f.add(X2('mask'))
        self.f.add(U1('dynModel'))
        self.f.add(U1('fixMode'))
        self.f.add(I4('fixedAlt'))
        self.f.add(U4('fixedAltVar'))
        self.f.add(I1('minElev'))
        self.f.add(U1('drLimit'))   # reserved
        self.f.add(U2('pDop'))
        self.f.add(U2('tDop'))
        self.f.add(U2('pAcc'))
        self.f.add(U2('tAcc'))
        self.f.add(U1('staticHoldThresh'))
        self.f.add(U1('dgpsTimeOut'))
        self.f.add(U1('cnoThreshNumSVs'))
        self.f.add(U1('cnoThresh'))
        self.f.add(U2('pAccAdr'))
        self.f.add(U2('staticHoldMaxDist'))
        self.f.add(U1('utcStandard'))
        self.f.add(Padding(5, 'res1'))
