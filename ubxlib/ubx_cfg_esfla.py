from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Fields, Padding, U1, I2


class UbxCfgEsfla_(UbxFrame):
    CID = UbxCID(0x06, 0x2f)
    NAME = 'UBX-CFG-ESFLA'

    TYPE_VRP_Antenna = 0
    TYPE_VRP_IMU = 1


class UbxCfgEsflaPoll(UbxCfgEsfla_):
    NAME = UbxCfgEsfla_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgEsfla(UbxCfgEsfla_):
    """
    Reponse frame to poll request

    Contains all lever arm configurations
    """
    def __init__(self):
        super().__init__()

        # fields defined in unpack()

    def unpack(self):
        # Dynamically build fields based on message length
        self.f = Fields()
        self.f.add(U1('version'))
        self.f.add(U1('numConfigs'))
        self.f.add(Padding(2, 'res1'))

        # Extract upto this place to read number of level arm configurations
        super().unpack()

        assert self.f.numConfigs <= 5

        # Build final list
        for lever in range(self.f.numConfigs):
            self.f.add(U1_LeverArmType(f'leverArmType_{lever}'))
            self.f.add(Padding(1, f'res2_{lever}'))
            self.f.add(I2(f'leverArmX_{lever}'))
            self.f.add(I2(f'leverArmY_{lever}'))
            self.f.add(I2(f'leverArmZ_{lever}'))

        super().unpack()

    def lever_arm(self, armType):
        data = None
        for lever in range(self.f.numConfigs):
            x = self.f.get(f'leverArmType_{lever}')
            if x.value == armType:
                data = {
                    'x': self.f.get(f'leverArmX_{lever}').value,
                    'y': self.f.get(f'leverArmY_{lever}').value,
                    'z': self.f.get(f'leverArmZ_{lever}').value
                }
                break

        return data


class UbxCfgEsflaSet(UbxCfgEsfla_):
    """
    Configuration frame to set individual lever arm
    """
    def __init__(self):
        super().__init__()

        self.f.add(U1('version'))
        self.f.add(U1('numConfigs'))
        self.f.add(Padding(2, 'res1'))

        self.f.add(U1_LeverArmType('leverArmType'))
        self.f.add(Padding(1, 'res2'))
        self.f.add(I2('leverArmX'))
        self.f.add(I2('leverArmY'))
        self.f.add(I2('leverArmZ'))

        self.f.version = 0
        self.f.numConfigs = 1

    def set(self, lever_arm_type, x, y, z):
        assert lever_arm_type <= UbxCfgEsflaSet.TYPE_VRP_IMU
        assert -1000 <= x <= 1000
        assert -1000 <= y <= 1000
        assert -1000 <= z <= 1000

        self.f.leverArmType = lever_arm_type
        self.f.leverArmX = x
        self.f.leverArmY = y
        self.f.leverArmZ = z


class U1_LeverArmType(U1):
    type_names = [
        'VRP-to-Antenna', 'VRP-to-IMU', 'IMU-to-Antenna', 'IMU-to-VRP', 'IMU-to-CRP'
    ]

    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        res = self.name + f': '
        if self.value < len(U1_LeverArmType.type_names):
            res += f'{U1_LeverArmType.type_names[self.value]} ({self.value})'
        else:
            res += '<invalid>'

        return res
