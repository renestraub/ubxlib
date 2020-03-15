import logging
import struct

from ubxlib.frame import UbxFrame, UbxPoll
from ubxlib.frame import U1


logger = logging.getLogger('gnss_tool')


class UbxUpdSosPoll(UbxPoll):
    CLASS = 0x09
    ID = 0x14
    NAME = 'UBX-CFG-SOS-POLL'

    def __init__(self):
        super().__init__()


class UbxUpdSos(UbxFrame):
    CLASS = 0x09
    ID = 0x14
    NAME = 'UBX-CFG-SOS'

    def __init__(self):
        super().__init__()

        self.add_field(U1('cmd'))
        self.add_field(U1('res1_1'))
        self.add_field(U1('res1_2'))
        self.add_field(U1('res1_3'))
        self.add_field(U1('response'))
        self.add_field(U1('res2_1'))
        self.add_field(U1('res2_2'))
        self.add_field(U1('res2_3'))


class UbxUpdSosAction(UbxFrame):
    CLASS = 0x09
    ID = 0x14
    NAME = 'UBX-CFG-SOS-ACTION'

    def __init__(self):
        super().__init__()

        self.add_field(U1('cmd'))
        self.add_field(U1('res1_1'))
        self.add_field(U1('res1_2'))
        self.add_field(U1('res1_3'))
