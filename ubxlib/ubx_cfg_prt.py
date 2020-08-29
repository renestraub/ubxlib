from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Padding, U1, X2, X4, U4


class UbxCfgPrt_(UbxFrame):
    CID = UbxCID(0x06, 0x00)
    NAME = 'UBX-CFG-PRT'

    PORTID_Uart = 1


class UbxCfgPrtPoll(UbxCfgPrt_):
    NAME = UbxCfgPrt_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

        self.f.add(U1('PortId'))


class UbxCfgPrtUart(UbxCfgPrt_):
    def __init__(self):
        super().__init__()

        self.f.add(U1('PortId'))
        self.f.add(Padding(1, 'res1'))
        self.f.add(X2('txReady'))
        self.f.add(X4_Mode('mode'))
        self.f.add(U4('baudRate'))

        self.f.add(X2_Proto('inProtoMask'))
        self.f.add(X2_Proto('outProtoMask'))
        self.f.add(X2('flags'))
        self.f.add(Padding(2, 'res2'))


class X2_Proto(X2):
    def __init__(self, name):
        super().__init__(name)

    def unpack(self, data):
        len = super().unpack(data)

        res = ''
        if self.value & 0x01:
            res += 'UBX'
        if self.value & 0x02:
            res += ', NMEA'
        if self.value & 0x04:
            res += ', RTCM'

        self.protocols = res
        return len

    def __str__(self):
        return f'{self.name}: {self.protocols}'


class X4_Mode(X4):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        res = self.name + ': '

        charlen = (self.value >> 6) & 0x03
        charlen_str = ['5', '6', '7', '8']
        res += f'{charlen_str[charlen]} bits'

        parity = (self.value >> 9) & 0x07
        parity_str = ['even', 'odd', '', 'reserved', 'none', 'none', 'reserved', 'reserved']
        res += f', {parity_str[parity]}'

        stopbits = (self.value >> 12) & 0x03
        stopbits_str = ['1', '1.5', '2', '0.5']
        res += f', {stopbits_str[stopbits]} stop bit(s)'

        return res
