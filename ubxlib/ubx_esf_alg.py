from .cid import UbxCID
from .frame import UbxFrame
from .types import I2, U1, U4, Fields, Padding


class UbxEsfAlg_(UbxFrame):
    CID = UbxCID(0x10, 0x14)
    NAME = 'UBX-ESF-ALG'


class UbxEsfAlgPoll(UbxEsfAlg_):
    NAME = UbxEsfAlg_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

    def _cls_response(self):
        return UbxEsfAlg


class UbxEsfAlg(UbxEsfAlg_):
    def __init__(self):
        super().__init__()

        self.f = Fields()
        self.f.add(U4('iTow'))
        self.f.add(U1('version'))
        self.f.add(U1_Flags('flags'))
        self.f.add(U1('error'))
        self.f.add(Padding(1, 'res1'))
        self.f.add(U4('yaw'))      # 1e-2, 0..+360
        self.f.add(I2('pitch'))    # 1e-2, -90..+90
        self.f.add(I2('roll'))     # 1e-2, -180..180


class UbxEsfResetAlgAction(UbxFrame):
    CID = UbxCID(0x10, 0x13)
    NAME = 'UBX-ESF-RESETALG'

    def __init__(self):
        super().__init__()


class U1_Flags(U1):
    status_strings = ['0: user defined/fixed angles', '1: roll/pitch alignment', '2: roll/pitch/yaw',
                      '3: coarse', '4: fine', '5', '6', '7']

    def __init__(self, name):
        super().__init__(name)

        self.status = 0
        self.autoMntAlgOn = 0

    def unpack(self, data):
        len = super().unpack(data)

        self.status = (self.value >> 1) & 0x07
        self.autoMntAlgOn = (self.value >> 0) & 0x01

        return len

    def __str__(self):
        res = self.name + ': '
        res += 'autoMntAlgn: '
        res += 'on, ' if self.autoMntAlgOn == 1 else 'off, '
        res += f'status: {U1_Flags.status_strings[self.status]}'
        return res
