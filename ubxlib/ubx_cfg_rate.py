from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import U2


class UbxCfgRate_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x08)
    NAME = 'UBX-CFG-RATE'


class UbxCfgRatePoll(UbxCfgRate_):
    NAME = UbxCfgRate_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgRate(UbxCfgRate_):
    def __init__(self):
        super().__init__()

        self.f.add(U2('measRate'))  # Time elapsed between two measuremnts in ms
        self.f.add(U2('navRate'))   # Number of measurements for NAV solution
        self.f.add(U2('timeRef'))

    def set_rate_in_hz(self, rate):
        # should not go beyond 10 Hz
        assert 1 <= rate <= 10
        self.f.measRate = int(1000 / rate)
        self.f.navRate = 1
