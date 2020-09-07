from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Padding, U1, U2, X2, X4


class UbxCfgNavx5_(UbxFrame):
    CID = UbxCID(0x06, 0x23)
    NAME = 'UBX-CFG-NAVX5'


class UbxCfgNavx5Poll(UbxCfgNavx5_):
    NAME = UbxCfgNavx5_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgNavx5(UbxCfgNavx5_):
    MASK1_AckAid = 1 << 10

    def __init__(self):
        super().__init__()

        self.f.add(U2('version'))
        self.f.add(X2('mask1'))
        self.f.add(X4('mask2'))
        self.f.add(Padding(2, 'res1'))
        self.f.add(U1('minSVs'))
        self.f.add(U1('maxSVs'))
        self.f.add(U1('minCN0'))
        self.f.add(Padding(1, 'res2'))
        self.f.add(U1('iniFix3D'))
        self.f.add(Padding(2, 'res3'))
        self.f.add(U1('ackAiding'))
        self.f.add(U2('wknRollover'))
        self.f.add(U1('sigAttenCompMode'))
        self.f.add(Padding(1, 'res4'))
        self.f.add(Padding(2, 'res5'))
        self.f.add(Padding(2, 'res6'))
        self.f.add(U1('usePPP'))
        self.f.add(U1('aopCfg'))
        self.f.add(Padding(2, 'res7'))
        self.f.add(U2('aopOrbMaxErr'))
        self.f.add(Padding(4, 'res8'))
        self.f.add(Padding(3, 'res9'))
        self.f.add(U1('useAdr'))
        self.f.add(Padding(2, 'res10'))
        self.f.add(Padding(2, 'res11'))
