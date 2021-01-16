from .cid import UbxCID
from .frame import UbxFrame
from .types import U1, U4, X2, X4, Padding


class UbxCfgPrt_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x00)
    NAME = 'UBX-CFG-PRT'

    PORTID_Uart = 1


class UbxCfgPrtPoll(UbxCfgPrt_):
    NAME = UbxCfgPrt_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

        self.f.add(U1('PortId'))

    def _cls_response(self):
        return UbxCfgPrtUart


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
            res = self.concat(res, 'UBX')
        if self.value & 0x02:
            res = self.concat(res, 'NMEA')
        if self.value & 0x04:
            res = self.concat(res, 'RTCM')

        self.protocols = res
        return len

    @staticmethod
    def concat(text, add):
        if len(text) == 0:
            text = add
        else:
            text += ', ' + add
        return text

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
