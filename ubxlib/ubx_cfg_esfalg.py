from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.types import Padding, X4, U4, I2


class UbxCfgEsfAlg_(UbxFrame):
    CID = UbxCID(0x06, 0x56)
    NAME = 'UBX-CFG-ESFALG'


class UbxCfgEsfAlgPoll(UbxCfgEsfAlg_):
    NAME = UbxCfgEsfAlg_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgEsfAlg(UbxCfgEsfAlg_):
    BITFIELD_doAutoMntAlg = 0x100

    def __init__(self):
        super().__init__()

        self.f.add(X4('bitfield'))  # u-blox describes as U4, bit is X4
        self.f.add(U4('yaw'))       # 1e-2
        self.f.add(I2('pitch'))     # 1e-2
        self.f.add(I2('roll'))      # 1e-2
