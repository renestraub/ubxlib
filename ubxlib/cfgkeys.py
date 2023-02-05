#
# Configuration Keys for UbxValGet, UbxValSet
#
import struct

from .types import Item


class KeyInfo():
    def __init__(self, name, signed=False):
        self.name = name
        self.signed = signed


class UbxKeyId(object):
    CFG_SIGNAL_GPS_ENA = 0x1031001f
    CFG_SIGNAL_GPS_L1CA_ENA = 0x10310001
    CFG_SIGNAL_SBAS_ENA = 0x10310020
    CFG_SIGNAL_SBAS_L1CA_ENA = 0x10310005
    CFG_SIGNAL_GAL_ENA = 0x10310021
    CFG_SIGNAL_GAL_E1_ENA = 0x10310007
    CFG_SIGNAL_BDS_ENA = 0x10310022
    CFG_SIGNAL_BDS_B1_ENA = 0x1031000d
    CFG_SIGNAL_GLO_ENA = 0x10310025
    CFG_SIGNAL_GLO_L1_ENA = 0x10310018
    CFG_SIGNAL_QZSS_ENA = 0x10310024
    CFG_SIGNAL_QZSS_L1CA_ENA = 0x10310012
    CFG_SIGNAL_QZSS_L1S_ENA = 0x10310014

    CFG_NMEA_PROTVER = 0x20930001
    CFG_UART1_BAUDRATE = 0x40520001

    CFG_NAVSPG_FIXMODE = 0x20110011
    CFG_NAVSPG_DYNMODEL = 0x20110021

    CFG_RATE_MEAS = 0x30210001
    CFG_RATE_NAV = 0x30210002
    CFG_RATE_NAV_PRIO = 0x20210004

    CFG_SFCORE_USE_SF = 0x10080001
    CFG_SFIMU_IMU_MNTALG_YAW = 0x4006002d
    CFG_SFIMU_IMU_MNTALG_PITCH = 0x3006002e
    CFG_SFIMU_IMU_MNTALG_ROLL = 0x3006002f

    # CFG-TP-*
    CFG_TP_PULSE_DEF = 0x20050023
    CFG_TP_PULSE_LENGTH_DEF = 0x20050030
    CFG_TP_TP2_ENA = 0x10050012
    CFG_TP_PERIOD_TP2 = 0x4005000d
    CFG_TP_LEN_TP2 = 0x4005000f
    CFG_TP_TIMEGRID_TP2 = 0x20050017
    CFG_TP_ALIGN_TO_TOW_TP2 = 0x10050015
    CFG_TP_USE_LOCKED_TP2 = 0x10050014
    CFG_TP_POL_TP2 = 0x10050016
    CFG_TP_PERIOD_LOCK_TP2 = 0x4005000e
    CFG_TP_LEN_LOCK_TP2 = 0x40050010

    KEY_INFO = {
        CFG_SIGNAL_GPS_ENA: KeyInfo("CFG-SIGNAL-GPS_ENA"),
        CFG_SIGNAL_GPS_L1CA_ENA: KeyInfo("CFG-SIGNAL-GPS_L1CA_ENA"),
        CFG_SIGNAL_SBAS_ENA: KeyInfo("CFG-SIGNAL-SBAS_ENA"),
        CFG_SIGNAL_SBAS_L1CA_ENA: KeyInfo("CFG-SIGNAL-SBAS_L1CA_ENA"),
        CFG_SIGNAL_GAL_ENA: KeyInfo("CFG-SIGNAL-GAL_ENA"),
        CFG_SIGNAL_GAL_E1_ENA: KeyInfo("CFG-SIGNAL-GAL_E1_ENA"),
        CFG_SIGNAL_BDS_ENA: KeyInfo("CFG-SIGNAL-BDS_ENA"),
        CFG_SIGNAL_BDS_B1_ENA: KeyInfo("CFG-SIGNAL-BDS_B1_ENA"),
        CFG_SIGNAL_GLO_ENA: KeyInfo("CFG-SIGNAL-GLO_ENA"),
        CFG_SIGNAL_GLO_L1_ENA: KeyInfo("CFG-SIGNAL-GLO_L1_ENA"),
        CFG_SIGNAL_QZSS_ENA: KeyInfo("CFG-SIGNAL-QZSS_ENA"),
        CFG_SIGNAL_QZSS_L1CA_ENA: KeyInfo("CFG-SIGNAL-QZSS_L1CA_ENA"),
        CFG_SIGNAL_QZSS_L1S_ENA: KeyInfo("CFG-SIGNAL-QZSS_L1S_ENA"),

        CFG_NMEA_PROTVER: KeyInfo("CFG-NMEA-PROTVER"),
        CFG_UART1_BAUDRATE: KeyInfo("CFG-UART1-BAUDRATE"),

        CFG_NAVSPG_FIXMODE: KeyInfo("CFG-NAVSPG-FIXMODE"),
        CFG_NAVSPG_DYNMODEL: KeyInfo("CFG-NAVSPG-DYNMODEL"),

        CFG_RATE_MEAS: KeyInfo("CFG-RATE_MEAS"),
        CFG_RATE_NAV: KeyInfo("CFG-RATE-NAV"),
        CFG_RATE_NAV_PRIO: KeyInfo("CFG-RATE-NAV_PRIO"),

        CFG_SFCORE_USE_SF: KeyInfo("CFG-SFCORE-USE-SF"),
        CFG_SFIMU_IMU_MNTALG_YAW: KeyInfo("CFG-SFIMU-IMU_MNTALG_YAW"),
        CFG_SFIMU_IMU_MNTALG_PITCH: KeyInfo("CFG-SFIMU-IMU_MNTALG_PITCH", True),    # Signed value
        CFG_SFIMU_IMU_MNTALG_ROLL: KeyInfo("CFG-SFIMU-IMU_MNTALG_ROLL", True),    # Signed value

        CFG_TP_PULSE_DEF: KeyInfo("CFG-TP-PULSE_DEF"),
        CFG_TP_PULSE_LENGTH_DEF: KeyInfo("CFG-TP-PULSE_LENGTH_DEF"),
        CFG_TP_TP2_ENA: KeyInfo("CFG-TP-TP2_ENA"),
        CFG_TP_PERIOD_TP2: KeyInfo("CFG-TP-PERIOD_TP2"),
        CFG_TP_LEN_TP2: KeyInfo("CFG-TP-LEN_TP2"),
        CFG_TP_TIMEGRID_TP2: KeyInfo("CFG-TP-TIMEGRID_TP2"),
        CFG_TP_ALIGN_TO_TOW_TP2: KeyInfo("CFG-TP-ALIGN_TO_TOW_TP2"),
        CFG_TP_USE_LOCKED_TP2: KeyInfo("CFG-TP-USE_LOCKED_TP2"),
        CFG_TP_POL_TP2: KeyInfo("CFG-TP-POL_TP2"),
        CFG_TP_PERIOD_LOCK_TP2: KeyInfo("CFG-TP-PERIOD_LOCK_TP2"),
        CFG_TP_LEN_LOCK_TP2: KeyInfo("CFG-TP-LEN_LOCK_TP2"),
    }

    @staticmethod
    def sign(key):
        if key in UbxKeyId.KEY_INFO:
            return UbxKeyId.KEY_INFO[key].signed
        else:
            return False

    @staticmethod
    def to_str(key):
        if key in UbxKeyId.KEY_INFO:
            return UbxKeyId.KEY_INFO[key].name
        else:
            return None


class CfgKeyData(Item):
    # Mapping of UBX header size information to bit sizes of value
    SIZE_FROM_BITS = {1: 1, 8: 2, 16: 3, 32: 4, 64: 5}
    BITS_FROM_SIZE = [0, 1, 8, 16, 32, 64, 0, 0]

    # Number of value bytes in UBX message for given bitlength
    # Note the special case for (one) bit values
    BYTES_FROM_BITS = {1: 1, 8: 1, 16: 2, 32: 4, 64: 8}

    def __init__(self, name, group_id=None, item_id=None, bits=0, value=None, signed=False):
        super().__init__(name)
        self.group_id = group_id
        self.item_id = item_id
        self.bits = bits
        self.signed = signed
        self.value = value

    @classmethod
    def from_key(cls, key, value=None):
        bits = CfgKeyData._bits_from_key(key)
        group_id = CfgKeyData._group_from_key(key)
        item_id = CfgKeyData._item_from_key(key)
        # Whether value type is signed int can't be determined from key information
        # Check key database
        signed = UbxKeyId.sign(key)
        return cls('<anon>', group_id, item_id, bits, value, signed)

    @staticmethod
    def _bits_from_key(header):
        size = (header >> 28) & 0x7
        return CfgKeyData.BITS_FROM_SIZE[size]

    @staticmethod
    def _bytes_for_size(bits):
        if bits in CfgKeyData.BYTES_FROM_BITS:
            return CfgKeyData.BYTES_FROM_BITS[bits]
        else:
            raise ValueError

    @staticmethod
    def _group_from_key(header):
        return (header >> 16) & 0xFF

    @staticmethod
    def _item_from_key(header):
        return (header >> 0) & 0xFFF

    @staticmethod
    def _build_header(group_id, item_id, bits):
        try:
            size = CfgKeyData.SIZE_FROM_BITS[bits]
        except KeyError:
            raise ValueError
        header = (size & 0x7) << 28
        header |= (group_id & 0xFF) << 16
        header |= (item_id & 0xFFF) << 0
        return header

    def pack(self):
        """
        Dedicated pack method for configuration item key and data
        Key is always U4, data can have 1..8 bytes depending on datatype

        @return: bytearray with packed data
        """
        if self.group_id < 0 or self.group_id > 0xFF:
            raise ValueError
        if self.item_id < 0 or self.item_id > 0xFFF:
            raise ValueError

        try:
            key = self._pack_keyid()    # Build 32 bit item key ID
            value = self._pack_value()  # Add variable length data
            data = key + value
        except struct.error:
            raise ValueError

        return data

    def _pack_keyid(self):
        header = CfgKeyData._build_header(self.group_id, self.item_id, self.bits)
        key = struct.pack('<I', header)  # 32 bit key, little endian
        return key

    def _pack_value(self):
        if self.bits == 1:
            value = struct.pack("<B", 1 if self.value else 0)
        elif self.bits == 8:
            if self.signed:
                value = struct.pack("<b", self.value)
            else:
                value = struct.pack("<B", self.value)
        elif self.bits == 16:
            if self.signed:
                value = struct.pack("<h", self.value)
            else:
                value = struct.pack("<H", self.value)
        elif self.bits == 32:
            if self.signed:
                value = struct.pack("<i", self.value)
            else:
                value = struct.pack("<I", self.value)
        elif self.bits == 64:
            if self.signed:
                value = struct.pack("<q", self.value)
            else:
                value = struct.pack("<Q", self.value)
        else:
            raise ValueError
        return value

    def unpack(self, data):
        """
        Unpacks configuration item key and data
        - Data length is dynamic and depends on key[30..28], invalid length raise ValueError

        @param data: bytearray to extract data from
        @return: number of bytes consumed
        """
        if len(data) < 4:
            raise ValueError

        results = struct.unpack('<I', data[:4])     # extract 32 unsigned bits in little endian mode
        key = results[0]
        data = data[4:]
        bytes_consumed = 4

        self.bits = CfgKeyData._bits_from_key(key)
        self.group_id = CfgKeyData._group_from_key(key)
        self.item_id = CfgKeyData._item_from_key(key)
        self.signed = UbxKeyId.sign(key)    # Signedness can't be decoded from data, query KeyId class

        try:
            bytes_consumed += self._unpack_value(data)
        except struct.error:
            raise ValueError

        return bytes_consumed

    def _unpack_value(self, data):
        bytes_needed = CfgKeyData._bytes_for_size(self.bits)
        if self.bits == 1:
            results = struct.unpack("<B", data[:bytes_needed])
            if results[0] == 0:
                self.value = False
            elif results[0] == 1:
                self.value = True
            else:
                raise ValueError
        elif self.bits == 8:
            if self.signed:
                results = struct.unpack("<b", data[:bytes_needed])
            else:
                results = struct.unpack("<B", data[:bytes_needed])
            self.value = results[0]
        elif self.bits == 16:
            if self.signed:
                results = struct.unpack("<h", data[:bytes_needed])
            else:
                results = struct.unpack("<H", data[:bytes_needed])
            self.value = results[0]
        elif self.bits == 32:
            if self.signed:
                results = struct.unpack("<i", data[:bytes_needed])
            else:
                results = struct.unpack("<I", data[:bytes_needed])
            self.value = results[0]
        elif self.bits == 64:
            if self.signed:
                results = struct.unpack("<q", data[:bytes_needed])
            else:
                results = struct.unpack("<Q", data[:bytes_needed])
            self.value = results[0]
        else:
            raise ValueError

        return bytes_needed

    def __str__(self):
        """
        Format a string of the form
        data1: key: CFG-TP-PULSE_DEF, bits: 8, value: 0 (0x00)
        """
        header = CfgKeyData._build_header(self.group_id, self.item_id, self.bits)
        key_name = UbxKeyId.to_str(header)

        res = self.name + ':'
        if key_name:
            res += f' key: {key_name}'
        else:
            res += f' group: 0x{self.group_id:02x}, item: 0x{self.item_id:03x}'

        res += f', bits: {self.bits}'
        if self.bits == 1:
            str = "True" if self.value else "False"
            res += f', value: {str}'
        elif self.bits == 8:
            if self.signed:
                res += f', value: {self.value:d}'
            else:
                res += f', value: {self.value:d} (0x{self.value:02x})'
        elif self.bits == 16:
            if self.signed:
                res += f', value: {self.value:d}'
            else:
                res += f', value: {self.value:d} (0x{self.value:04x})'
        elif self.bits == 32:
            if self.signed:
                res += f', value: {self.value:d}'
            else:
                res += f', value: {self.value:d} (0x{self.value:08x})'
        elif self.bits == 64:
            if self.signed:
                res += f', value: {self.value:d}'
            else:
                res += f', value: {self.value:d} (0x{self.value:016x})'
        else:
            raise ValueError
        return res


class CfgKeyValues:
    @staticmethod
    def from_keyvalues(key_vals: list):
        cfg_keyvals = [CfgKeyData.from_key(key, value) for key, value in key_vals]
        return cfg_keyvals
