from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.types import Fields, Padding, X1, U1, U4


class UbxEsfStatus_(UbxFrame):
    CID = UbxCID(0x10, 0x10)
    NAME = 'UBX-ESF-STATUS'


class UbxEsfStatusPoll(UbxEsfStatus_):
    NAME = UbxEsfStatus_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxEsfStatus(UbxEsfStatus_):
    def __init__(self):
        super().__init__()

        # fields define in unpack()

    def unpack(self):
        # Dynamically build fields based on message length
        self.f = Fields()
        self.f.add(U4('iTow'))
        self.f.add(U1('version'))
        self.f.add(X1('initStatus'))
        self.f.add(Padding(6, 'res1'))
        self.f.add(U1('status'))
        self.f.add(Padding(2, 'res2'))
        self.f.add(U1('numSens'))

        # Extract upto this place to read number of sensors
        super().unpack()

        # Build final list
        for sensor in range(self.f.numSens):
            self.f.add(X1(f'sensStatus1_{sensor}'))
            self.f.add(X1(f'sensStatus2_{sensor}'))
            self.f.add(U1(f'freq_{sensor}'))
            self.f.add(X1(f'faults_{sensor}'))

        super().unpack()
