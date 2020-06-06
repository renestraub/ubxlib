
from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.types import X4


class UbxCfgCfg_(UbxFrame):
    NAME = 'UBX-CFG-CFG'
    CID = UbxCID(0x06, 0x09)


class UbxCfgCfgAction(UbxCfgCfg_):
    NAME = UbxCfgCfg_.NAME + '-ACTION'

    # masks
    MASK_IoPort = 0x0001
    MASK_MsgConf = 0x0002
    MASK_InfMsg = 0x0004
    MASK_NavConf = 0x0008   # NAV parameters, ADR/UDR
    MASK_RxmConf = 0x0010   # GNSS Systems, Timepulse 5
    MASK_SenConf = 0x0100
    MASK_RinvConf = 0x0200
    MASK_AntConf = 0x0400
    MASK_LogConf = 0x0800
    MASK_FtsConf = 0x1000
    MASK_All = 0x1F1F

    def __init__(self):
        super().__init__()

        self.f.add(X4('clearMask'))
        self.f.add(X4('saveMask'))
        self.f.add(X4('loadMask'))

    def save(self, settings):
        self.f.saveMask = settings
        self.f.clearMask = 0
        self.f.loadMask = 0

    def reset(self, settings):
        self.f.clearMask = settings
        self.f.loadMask = settings
        self.f.saveMask = 0
