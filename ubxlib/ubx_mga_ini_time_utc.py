import time
import datetime

from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Padding, U1, U2, U4, X1, I1


class UbxMgaIniTimeUtc_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_MGA, 0x40)
    NAME = 'UBX-MGA-INI-TIME_UTC'


class UbxMgaIniTimeUtc(UbxMgaIniTimeUtc_):
    def __init__(self):
        super().__init__()

        self.f.add(U1('type'))
        self.f.add(U1('version'))
        self.f.add(X1('ref'))

        self.f.add(I1('leapSecs'))
        self.f.add(U2('year'))
        self.f.add(U1('month'))
        self.f.add(U1('day'))
        self.f.add(U1('hour'))
        self.f.add(U1('minute'))
        self.f.add(U1('second'))
        self.f.add(Padding(1, 'res1'))
        self.f.add(U4('ns'))

        self.f.add(U2('tAccS'))
        self.f.add(Padding(2, 'res2'))
        self.f.add(U4('tAccNs'))

    def set_datetime(self, dt):
        self.f.type = 0x10      # 0x10 for UTC time format
        self.f.version = 0x00
        self.f.ref = 0x00       # receipt of message will be inaccurate

        self.f.leapSecs = -128   # number of leap seconds is unknown

        self.f.year = dt.year
        self.f.month = dt.month
        self.f.day = dt.day
        self.f.hour = dt.hour
        self.f.minute = dt.minute
        self.f.second = dt.second
        self.f.ns = 0   # dt.microsecond * 1000.0

        self.f.tAccS = 10
        self.f.tAccNs = 0  # 999999999
        # Accuracy 0 taken from u-center example
        # not sure whether this is correct
