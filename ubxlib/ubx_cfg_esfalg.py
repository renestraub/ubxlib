from .cid import UbxCID
from .frame import UbxFrame
from .types import I2, U4, X4


class UbxCfgEsfAlg_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x56)
    NAME = 'UBX-CFG-ESFALG'


class UbxCfgEsfAlgPoll(UbxCfgEsfAlg_):
    NAME = UbxCfgEsfAlg_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

    def _cls_response(self):
        return UbxCfgEsfAlg


class UbxCfgEsfAlg(UbxCfgEsfAlg_):
    BITFIELD_doAutoMntAlg = 0x100

    def __init__(self):
        super().__init__()

        self.f.add(X4('bitfield'))  # u-blox describes as U4, bit is X4
        self.f.add(U4('yaw'))       # 1e-2, 0..360°
        self.f.add(I2('pitch'))     # 1e-2, -90..90°
        self.f.add(I2('roll'))      # 1e-2, -180..180°

    # TODO:
    # def enableAutoAlignment()
    # def disableAutoAlignment()
