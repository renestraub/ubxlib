from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.types import Fields, Padding, X1, U1, U4


class UbxEsfStatus_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_ESF, 0x10)
    NAME = 'UBX-ESF-STATUS'


class UbxEsfStatusPoll(UbxEsfStatus_):
    NAME = UbxEsfStatus_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

    def _cls_response(self):
        return UbxEsfStatus


class UbxEsfStatus(UbxEsfStatus_):
    def __init__(self):
        super().__init__()

        # fields defined in unpack()

    def unpack(self):
        # Dynamically build fields based on message length
        self.f = Fields()
        self.f.add(U4('iTow'))
        self.f.add(U1('version'))
        self.f.add(X1_InitStatus1('initStatus1'))
        self.f.add(X1_InitStatus2('initStatus2'))
        self.f.add(Padding(5, 'res1'))
        self.f.add(U1_FusionMode('fusionMode'))
        self.f.add(Padding(2, 'res2'))
        self.f.add(U1('numSens'))

        # Extract upto this place to read number of sensors
        super().unpack()

        # Build final list
        for sensor in range(self.f.numSens):
            self.f.add(X1_SensStatus1(f'sensStatus1_{sensor}'))
            self.f.add(X1_SensStatus2(f'sensStatus2_{sensor}'))
            self.f.add(U1(f'freq_{sensor}'))
            self.f.add(X1(f'faults_{sensor}'))

        super().unpack()


class X1_InitStatus1(X1):
    wt_init_strings = ['off', 'initializing', 'initialized', '<invalid>']
    mnt_alg_strings = ['off', 'initializing', 'initialized', 'initialized',
                       '<invalid>', '<invalid>', '<invalid>', '<invalid>']
    ins_init_strings = ['off', 'initializing', 'initialized', '<invalid>']

    def __init__(self, name):
        super().__init__(name)

        self.insInitStatus = 0
        self.mntAlgStatus = 0
        self.wtInitStatus = 0

    def unpack(self, data):
        len = super().unpack(data)

        self.insInitStatus = (self.value >> 5) & 0x03
        self.mntAlgStatus = (self.value >> 2) & 0x07
        self.wtInitStatus = (self.value >> 0) & 0x03

        return len

    def __str__(self):
        res = self.name + ': '
        res += f'wt: {X1_InitStatus1.wt_init_strings[self.wtInitStatus]}, '
        res += f'mntAlg: {X1_InitStatus1.mnt_alg_strings[self.mntAlgStatus]}, '
        res += f'ins: {X1_InitStatus1.ins_init_strings[self.insInitStatus]}'
        return res


class X1_InitStatus2(X1):
    imu_init_strings = ['off', 'initializing', 'initialized', '<invalid>']

    def __init__(self, name):
        super().__init__(name)

        self.ins_init_status = 0

    def unpack(self, data):
        len = super().unpack(data)

        self.ins_init_status = (self.value >> 0) & 0x03

        return len

    def __str__(self):
        res = self.name + ': '
        res += f'imu: {X1_InitStatus2.imu_init_strings[self.ins_init_status]}'
        return res


class U1_FusionMode(U1):
    fusion_mode_strings = ['init', 'fusion', 'suspend', 'disabled']

    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        res = self.name + ': '
        if self.value < len(U1_FusionMode.fusion_mode_strings):
            res += U1_FusionMode.fusion_mode_strings[self.value]
        else:
            res += '<invalid>'
        return res


class X1_SensStatus1(X1):
    sensor_types = ['none', '', '', '', '',
                    'gyro-z',
                    'front-left wt', 'front-right wt', 'rear-left wt', 'rear-right wt',
                    'single-tick', 'speed',
                    'gyro-temp',
                    'gyro-y', 'gyro-x', '',
                    'accel-x', 'accel-y', 'accel-z'
                    ]

    def __init__(self, name):
        super().__init__(name)

        self.type = 0
        self.used = 0
        self.ready = 0

    def unpack(self, data):
        len = super().unpack(data)

        self.type = (self.value >> 0) & 0x3F
        self.used = (self.value >> 6) & 0x01
        self.ready = (self.value >> 7) & 0x01

        return len

    def __str__(self):
        res = self.name + ': '
        if self.type < len(X1_SensStatus1.sensor_types):
            res += f'{X1_SensStatus1.sensor_types[self.type]}, '
        else:
            res += '<invalid>, '
        res += 'used, ' if self.used == 1 else 'unused, '
        res += 'ready' if self.ready == 1 else 'not ready'
        return res


class X1_SensStatus2(X1):
    calib_strings = ['not calibrated', 'calibrating', 'calibrated', 'calibrated 2']
    time_strings = ['no data', 'first byte', 'event input', 'time tag']

    def __init__(self, name):
        super().__init__(name)

        self.calibStatus = 0
        self.timeStatus = 0

    def unpack(self, data):
        len = super().unpack(data)

        self.calibStatus = (self.value >> 0) & 0x03
        self.timeStatus = (self.value >> 2) & 0x03

        return len

    def __str__(self):
        res = self.name + ': '
        res += f'calibStatus: {X1_SensStatus2.calib_strings[self.calibStatus]}, '
        res += f'timeStatus: {X1_SensStatus2.time_strings[self.timeStatus]}'
        return res
