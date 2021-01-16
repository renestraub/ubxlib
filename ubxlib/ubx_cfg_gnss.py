from .cid import UbxCID
from .frame import UbxFrame
from .types import U1, X4, Fields, Padding


class UbxCfgGnss_(UbxFrame):
    CID = UbxCID(UbxCID.CLASS_CFG, 0x3E)
    NAME = 'UBX-CFG-GNSS'


class UbxCfgGnssPoll(UbxCfgGnss_):
    NAME = UbxCfgGnss_.NAME + '-POLL'

    def __init__(self):
        super().__init__()

    def _cls_response(self):
        return UbxCfgGnss


class UbxCfgGnss(UbxCfgGnss_):
    GNSS_GPS = 0        # US GPS, worldwide
    GNSS_SBAS = 1       # Satellite Based Augmentation System
    GNSS_Galileo = 2    # European
    GNSS_BeiDou = 3     # Chinese
    GNSS_IMES = 4       # Japanese Indoor System
    GNSS_QZSS = 5       # Japanse, Focus Japan, also Australia
    GNSS_GLONASS = 6    # Russian
    GNSS_IRNSS = 7      # Indian, not (yet) supported on NEO-M8

    def __init__(self):
        super().__init__()

        # fields defined in unpack as they are dynamic

    def unpack(self):
        # Dynamically build fields based on message length
        self.f = Fields()
        self.f.add(U1('msgVer'))
        self.f.add(U1('numTrkChHw'))
        self.f.add(U1('numTrkChUse'))
        self.f.add(U1('numConfigBlocks'))

        # Extract upto this place to read number of config blocks
        super().unpack()

        # TODO: Check extra length against numConfigBlocks
        # TODO: raise on mismatch
        """
        extra_length = len(self.data) - 40
        extra_info = int(extra_length / 30)
        """

        # TODO: check nested fields -> unit test
        for i in range(self.f.numConfigBlocks):
            self.f.add(U1_GnssId(f'gnssId_{i}'))
            self.f.add(U1(f'resTrkCh_{i}'))
            self.f.add(U1(f'maxTrkCh_{i}'))
            self.f.add(Padding(1, f'res1_{i}'))
            self.f.add(X4_Flags(f'flags_{i}'))

        super().unpack()

    def gps_glonass(self):
        self.enable_gnss(UbxCfgGnss.GNSS_GPS)
        self.enable_gnss(UbxCfgGnss.GNSS_SBAS)
        self.enable_gnss(UbxCfgGnss.GNSS_GLONASS)

        self.disable_gnss(UbxCfgGnss.GNSS_Galileo)
        self.disable_gnss(UbxCfgGnss.GNSS_BeiDou)
        self.disable_gnss(UbxCfgGnss.GNSS_IMES)
        self.disable_gnss(UbxCfgGnss.GNSS_QZSS)
        # self.disable_gnss(UbxCfgGnss.GNSS_IRNSS)

    def gps_galileo_beidou(self):
        self.enable_gnss(UbxCfgGnss.GNSS_GPS)
        self.enable_gnss(UbxCfgGnss.GNSS_SBAS)
        self.enable_gnss(UbxCfgGnss.GNSS_Galileo)
        self.enable_gnss(UbxCfgGnss.GNSS_BeiDou)

        self.disable_gnss(UbxCfgGnss.GNSS_IMES)
        self.disable_gnss(UbxCfgGnss.GNSS_QZSS)
        self.disable_gnss(UbxCfgGnss.GNSS_GLONASS)
        # self.disable_gnss(UbxCfgGnss.GNSS_IRNSS)

    def enable_gnss(self, system):
        assert 0 <= system <= UbxCfgGnss.GNSS_IRNSS
        pos = self._find_entry(system)
        if pos:
            field = f'flags_{system}'
            self.f._fields[field].enable()

    def disable_gnss(self, system):
        assert 0 <= system <= UbxCfgGnss.GNSS_IRNSS
        pos = self._find_entry(system)
        if pos:
            field = f'flags_{system}'
            self.f._fields[field].disable()

    def _find_entry(self, system):
        assert 0 <= system <= UbxCfgGnss.GNSS_IRNSS

        for i in range(self.f.numConfigBlocks):
            field_name = f'gnssId_{i}'
            field = self.f.get(field_name)
            if field.value == system:
                return i


class U1_GnssId(U1):
    gnss_system_names = ['gps', 'sbas', 'galileo', 'beidou', 'imes', 'qzss', 'glonass', 'irnss']

    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        res = self.name + ': '
        if self.value < len(U1_GnssId.gnss_system_names):
            res += U1_GnssId.gnss_system_names[self.value]
        else:
            res += '<invalid>'
        return res


class X4_Flags(X4):
    def __init__(self, name):
        super().__init__(name)

    def enable(self):
        self.value |= 0x1

    def disable(self):
        self.value &= ~0x1

    def __str__(self):
        enabled = (self.value >> 0) & 0x1

        res = self.name + ': '
        res += 'enabled' if enabled else 'disabled'
        return res
