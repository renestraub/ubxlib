from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Padding, CH, U1, I2, I4, X1, X4


class UbxCfgNmea_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x17)
    NAME = 'UBX-CFG-NMEA'


class UbxCfgNmeaPoll(UbxCfgNmea_):
    NAME = UbxCfgNmea_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgNmea(UbxCfgNmea_):
    def __init__(self):
        super().__init__()

        self.f.add(X1('filter'))
        self.f.add(U1('nmeaVersion'))
        self.f.add(U1('numSV'))
        self.f.add(X1('flags'))
        self.f.add(X4('gnssToFilter'))
        self.f.add(U1('svNumbering'))
        self.f.add(U1('mainTalkerId'))
        self.f.add(U1('gsvTalkerId'))
        self.f.add(U1('version'))
        self.f.add(CH(2, 'bdsTalkerId'))
        self.f.add(Padding(6, 'res1'))
