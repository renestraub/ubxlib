from .cid import UbxCID
from .frame import UbxFrame
from .types import I2, I4, U1, X4, Padding


class UbxCfgTp5_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x31)
    NAME = 'UBX-CFG-TP5'


class UbxCfgTp5Poll(UbxCfgTp5_):
    NAME = UbxCfgTp5_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

        self.f.add(U1('tpIdx'))

    def _cls_response(self):
        return UbxCfgTp5


class UbxCfgTp5(UbxCfgTp5_):
    def __init__(self):
        super().__init__()

        self.f.add(U1('tpIdx'))
        self.f.add(U1('version'))
        self.f.add(Padding(2, 'res1'))
        self.f.add(I2('antCableDelay'))
        self.f.add(I2('rfGroupDelay'))
        self.f.add(I4('freqPeriod'))
        self.f.add(I4('freqPeriodLock'))
        self.f.add(I4('pulseLenRatio'))
        self.f.add(I4('pulseLenRatioLock'))
        self.f.add(I4('userConfigDelay'))
        self.f.add(X4('flags'))
