from .cid import UbxCID
from .frame import UbxFrame
from .types import U1, X2, Padding


class UbxCfgRst_(UbxFrame):
    NAME = 'UBX-CFG-RST'
    CID = UbxCID(UbxCID.CLASS_CFG, 0x04)


class UbxCfgRstAction(UbxCfgRst_):
    """
    Note: This message is not acknowledged
    """
    NAME = UbxCfgRst_.NAME + '-ACTION'

    # navBbrMask
    HOT_START = 0x0000
    WARM_START = 0x0001
    COLD_START = 0xFFFF

    # resetMode
    IMMEDIATE_HW_RESET = 0x00
    SW_RESET = 0x01
    HW_RESET = 0x04
    STOP = 0x08
    START = 0x09

    def __init__(self):
        super().__init__()

        self.f.add(X2('navBbrMask'))
        self.f.add(U1('resetMode'))
        self.f.add(Padding(1, 'res1'))

    def warm_start(self):
        self.f.resetMode = UbxCfgRstAction.SW_RESET
        self.f.navBbrMask = UbxCfgRstAction.WARM_START

    def cold_start(self):
        self.f.resetMode = UbxCfgRstAction.SW_RESET
        self.f.navBbrMask = UbxCfgRstAction.COLD_START

    def start(self):
        self.f.resetMode = UbxCfgRstAction.START
        self.f.navBbrMask = UbxCfgRstAction.HOT_START

    def stop(self):
        self.f.resetMode = UbxCfgRstAction.STOP
        self.f.navBbrMask = UbxCfgRstAction.HOT_START
