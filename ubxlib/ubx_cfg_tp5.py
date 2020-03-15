from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.types import U1, I2, I4, X4


class UbxCfgTp5Poll(UbxFrame):
    CID = UbxCID(0x06, 0x31)
    NAME = 'UBX-CFG-TP5-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgTp5(UbxFrame):
    CID = UbxCID(0x06, 0x31)
    NAME = 'UBX-CFG-TP5'

    def __init__(self):
        super().__init__()

        self.f.add(U1('tpIdx'))
        self.f.add(U1('version'))
        self.f.add(U1('res1_1'))
        self.f.add(U1('res1_2'))
        self.f.add(I2('antCableDelay'))
        self.f.add(I2('rfGroupDelay'))
        self.f.add(I4('freqPeriod'))
        self.f.add(I4('freqPeriodLock'))
        self.f.add(I4('pulseLenRatio'))
        self.f.add(I4('pulseLenRatioLock'))
        self.f.add(I4('userConfigDelay'))
        self.f.add(X4('flags'))
