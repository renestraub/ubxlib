from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.types import Fields, Padding, U1, X4


class UbxCfgGnss_(UbxFrame):
    CID = UbxCID(0x06, 0x3E)
    NAME = 'UBX-CFG-GNSS'


class UbxCfgGnssPoll(UbxCfgGnss_):
    NAME = UbxCfgGnss_.NAME + '-POLL'

    def __init__(self):
        super().__init__()


class UbxCfgGnss(UbxCfgGnss_):
    GNSS_GPS = 0        # US GPS, worldwide
    GNSS_SBAS = 1       # Satellite Based Augmentation System
    GNSS_Galileo = 2    # European
    GNSS_BeiDou = 3     # Chinese
    GNSS_IMES = 4       # Japanese Indoor System
    GNSS_GZSS = 5       # Japanse, Focus Japan, also Australia
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
            self.f.add(U1(f'gnssId_{i}'))
            self.f.add(U1(f'resTrkCh_{i}'))
            self.f.add(U1(f'maxTrkCh_{i}'))
            self.f.add(Padding(1, f'res1_{i}'))
            self.f.add(X4(f'flags_{i}'))    # Bit 0: enable

        super().unpack()

    def gps_glonass(self):
        self.enable_gnss(UbxCfgGnss.GNSS_GPS)
        self.enable_gnss(UbxCfgGnss.GNSS_SBAS)
        self.enable_gnss(UbxCfgGnss.GNSS_GLONASS)

        self.disable_gnss(UbxCfgGnss.GNSS_Galileo)
        self.disable_gnss(UbxCfgGnss.GNSS_BeiDou)
        self.disable_gnss(UbxCfgGnss.GNSS_IMES)
        self.disable_gnss(UbxCfgGnss.GNSS_GZSS)
        # self.disable_gnss(UbxCfgGnss.GNSS_IRNSS)

    def gps_galileo_beidou(self):
        self.enable_gnss(UbxCfgGnss.GNSS_GPS)
        self.enable_gnss(UbxCfgGnss.GNSS_SBAS)
        self.enable_gnss(UbxCfgGnss.GNSS_Galileo)
        self.enable_gnss(UbxCfgGnss.GNSS_BeiDou)

        self.disable_gnss(UbxCfgGnss.GNSS_IMES)
        self.disable_gnss(UbxCfgGnss.GNSS_GZSS)
        self.disable_gnss(UbxCfgGnss.GNSS_GLONASS)
        # self.disable_gnss(UbxCfgGnss.GNSS_IRNSS)

    def enable_gnss(self, system):
        assert 0 <= system <= 7
        # TODO: Do not assume system == field entry, rather
        # lookup gnssId
        field = f'flags_{system}'
        flag = self.f._fields[field].value
        # print(f'{flag:08x}')
        flag |= 1
        self.f._fields[field].value = flag

    def disable_gnss(self, system):
        assert 0 <= system <= 7
        # TODO: Do not assume system == field entry, rather
        # lookup gnssId
        field = f'flags_{system}'
        flag = self.f._fields[field].value
        # print(f'{flag:08x}')
        flag &= ~1
        self.f._fields[field].value = flag
