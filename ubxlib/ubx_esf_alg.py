from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.types import Fields, Padding, X1, U1, U4, I2, I4


class UbxEsfAlg_(UbxFrame):
    CID = UbxCID(0x10, 0x14)
    NAME = 'UBX-ESF-ALG'


class UbxEsfAlgPoll(UbxEsfAlg_):
    NAME = UbxEsfAlg_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxEsfAlg(UbxEsfAlg_):
    def __init__(self):
        super().__init__()

        self.f = Fields()
        self.f.add(U4('iTow'))
        self.f.add(U1('version'))
        self.f.add(X1('bitfield0'))
        self.f.add(Padding(2, 'res1'))
        self.f.add(I4('yaw'))      # 1e-1 -> more likely 1e-2
        self.f.add(I2('pitch'))     # 1e-1
        self.f.add(I2('roll'))       # 1e-1

        # TODO: Check if properly documented.
        # 30c74a22 01 00 0000 64000000 c800 2c01
        # Does not report proper yaw, pitch, roll values when manually configured
        # yaw displays roll
        # pitch displays pitch
        # roll displays 0 (yaw?)

    def unpack(self):
        import binascii
        print(binascii.hexlify(self.data))
        return super().unpack()


class UbxEsfResetAlgAction(UbxFrame):
    CID = UbxCID(0x10, 0x13)
    NAME = 'UBX-ESF-RESETALG'

    def __init__(self):
        super().__init__()
