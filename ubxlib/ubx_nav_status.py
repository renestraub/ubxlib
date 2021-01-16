from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Fields, X1, U1, U4


class UbxNavStatus_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_NAV, 0x03)
    NAME = 'UBX-NAV-STATUS'


class UbxNavStatusPoll(UbxNavStatus_):
    NAME = UbxNavStatus_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

    def _cls_response(self):
        return UbxNavStatus


class UbxNavStatus(UbxNavStatus_):
    def __init__(self):
        super().__init__()

        self.f = Fields()
        self.f.add(U4('iTow'))
        self.f.add(U1_GpsFix('gpsFix'))
        self.f.add(X1_Flags('flags'))
        self.f.add(X1('fixStat'))
        self.f.add(X1('flags2'))

        self.f.add(U4('ttff'))
        self.f.add(U4('msss'))


class U1_GpsFix(U1):
    gps_fix_strings = ['no fix', 'DR only', '2D-fix', '3D-fix', 'GPS+DR fix', 'Time only fix']

    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        res = self.name + ': '
        if self.value < len(U1_GpsFix.gps_fix_strings):
            res += U1_GpsFix.gps_fix_strings[self.value]
        else:
            res += '<invalid>'
        return res


class X1_Flags(X1):
    def __init__(self, name):
        super().__init__(name)

        self.gpsFixOk = False   # 1 = position and velocity valid and within DOP and ACC Masks.
        self.diffSoln = False   # 1 = differential corrections were applied
        self.wknSet = False
        self.twoSet = False

    def unpack(self, data):
        len = super().unpack(data)

        self.gpsFixOk = ((self.value >> 0) & 0x01) == 0x01
        self.diffSoln = ((self.value >> 1) & 0x01) == 0x01
        self.wknSet = ((self.value >> 2) & 0x01) == 0x01
        self.twoSet = ((self.value >> 3) & 0x01) == 0x01

        return len

    def __str__(self):
        res = self.name + ': '
        res += f'gpsFixOk: {self.gpsFixOk}, '
        res += f'diffSoln: {self.diffSoln}, '
        res += f'wknSet: {self.wknSet}, '
        res += f'towSet: {self.twoSet}'
        return res
