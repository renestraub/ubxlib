import logging
import struct

from ubxlib.frame import UbxFrame, UbxPoll
from ubxlib.frame import U1, I2, I4, X4


logger = logging.getLogger('gnss_tool')


class UbxCfgTp5Poll(UbxPoll):
    CLASS = 0x06
    ID = 0x31
    NAME = 'UBX-CFG-TP5-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgTp5(UbxFrame):
    CLASS = 0x06
    ID = 0x31
    NAME = 'UBX-CFG-TP5'

    """
    @classmethod
    def construct(cls, data):
        obj = cls()
        obj.data = data
        obj.unpack()
        return obj
    """

    def __init__(self):
        # super().__init__(msg.cls, msg.id, msg.data)
        super().__init__()

        self.add_field(U1('tpIdx'))
        self.add_field(U1('version'))
        self.add_field(U1('res1_1'))
        self.add_field(U1('res1_2'))
        self.add_field(I2('antCableDelay'))
        self.add_field(I2('rfGroupDelay'))
        self.add_field(I4('freqPeriod'))
        self.add_field(I4('freqPeriodLock'))
        self.add_field(I4('pulseLenRatio'))
        self.add_field(I4('pulseLenRatioLock'))
        self.add_field(I4('userConfigDelay'))
        self.add_field(X4('flags'))
