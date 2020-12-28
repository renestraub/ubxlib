from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import U1


class UbxAckAck(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_ACK, 0x01)
    NAME = 'UBX-ACK-ACK'

    def __init__(self):
        super().__init__()

        self.f.add(U1('clsId'))
        self.f.add(U1('msgId'))


class UbxAckNak(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_ACK, 0x00)
    NAME = 'UBX-ACK-NAK'

    def __init__(self):
        super().__init__()

        self.f.add(U1('clsId'))
        self.f.add(U1('msgId'))
