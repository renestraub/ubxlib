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
        self.f.add(Padding(7, 'res1'))
        self.f.add(U1('fusionMode'))
        self.f.add(Padding(2, 'res2'))
        self.f.add(U1('numSens'))

        """
        extra_length = len(self.data) - 40
        extra_info = int(extra_length / 30)
        for i in range(extra_info):
            self.f.add(CH(30, f'extension_{i}'))
        """
        super().unpack()
        print(self.f.numSens)

        for sensor in range(self.f.numSens):
            self.f.add(X1(f'sensStatus1_{sensor}'))
            self.f.add(X1(f'sensStatus2_{sensor}'))
            self.f.add(U1(f'freq_{sensor}'))
            self.f.add(X1(f'faults_{sensor}'))

        super().unpack()
