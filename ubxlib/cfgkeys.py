#
# Configuration Keys for UbxValGet, UbxValSet
#
import struct

from .types import Item


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

    CFG_NAVSPG_DYNMODEL = 0x20110021

    CFG_RATE_MEAS = 0x30210001

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

    KEY_NAMES = {
        0x1031001f: "CFG-SIGNAL-GPS_ENA",
        0x10310001: "CFG-SIGNAL-GPS_L1CA_ENA",
        0x10310020: "CFG-SIGNAL-SBAS_ENA",
        0x10310005: "CFG-SIGNAL-SBAS_L1CA_ENA",
        0x10310021: "CFG-SIGNAL-GAL_ENA",
        0x10310007: "CFG-SIGNAL-GAL_E1_ENA",
        0x10310022: "CFG-SIGNAL-BDS_ENA",
        0x1031000d: "CFG-SIGNAL-BDS_B1_ENA",
        0x10310025: "CFG-SIGNAL-GLO_ENA",
        0x10310018: "CFG-SIGNAL-GLO_L1_ENA",

        0x20110021: "CFG-NAVSPG-DYNMODEL",

        0x30210001: "CFG-RATE_MEAS",

        0x4006002d: "CFG-SFIMU-IMU_MNTALG_YAW",
        0x3006002e: "CFG-SFIMU-IMU_MNTALG_PITCH",
        0x3006002f: "CFG-SFIMU-IMU_MNTALG_ROLL",

        0x20050023: "CFG-TP-PULSE_DEF",
        0x20050030: "CFG-TP-PULSE_LENGTH_DEF",
        0x10050012: "CFG-TP-TP2_ENA",
        0x4005000d: "CFG-TP-PERIOD_TP2",
        0x4005000f: "CFG-TP-LEN_TP2",
        0x20050017: "CFG-TP-TIMEGRID_TP2",
        0x10050015: "CFG-TP-ALIGN_TO_TOW_TP2",
        0x10050014: "CFG-TP-USE_LOCKED_TP2",
        0x10050016: "CFG-TP-POL_TP2",
        0x4005000e: "CFG-TP-PERIOD_LOCK_TP2",
        0x40050010: "CFG-TP-LEN_LOCK_TP2",
    }

    @staticmethod
    def to_str(key):
        if key in UbxKeyId.KEY_NAMES:
            return UbxKeyId.KEY_NAMES[key]
        else:
            return None


class CfgKeyData(Item):
    SIZE_FROM_BITS = { 1: 1, 8: 2, 16: 3, 32: 4, 64: 5 }
    BITS_FROM_SIZE = [ 0, 1, 8, 16, 32, 64, 0, 0 ]

    def __init__(self, name, group_id=None, item_id=None, bits=0, value=None):
        super().__init__(name)
        self.group_id = group_id
        self.item_id = item_id
        self.bits = bits
        self.value = value

    @classmethod
    def from_key(cls, key, value=None):
        bits = CfgKeyData.bits_from_key(key)
        group_id = CfgKeyData.group_from_key(key)
        item_id = CfgKeyData.item_from_key(key)
        return cls('<anon>', group_id, item_id, bits, value)

    # @classmethod
    # def from_u8(cls, name, group_id=None, item_id=None, value=None):
    #     return cls(name, group_id, item_id, 8, value)

    # @classmethod
    # def from_u16(cls, name, group_id=None, item_id=None, value=None):
    #     return cls(name, group_id, item_id, 16, value)

    # @classmethod
    # def from_u32(cls, name, group_id=None, item_id=None, value=None):
    #     return cls(name, group_id, item_id, 32, value)

    @staticmethod
    def bits_from_key(header):
        size = (header >> 28) & 0x7
        return CfgKeyData.BITS_FROM_SIZE[size]

    @staticmethod
    def group_from_key(header):
        return (header >> 16) & 0xFF

    @staticmethod
    def item_from_key(header):
        return (header >> 0) & 0xFFF

    @staticmethod
    def build_header(group_id, item_id, bits):
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

        header = CfgKeyData.build_header(self.group_id, self.item_id, self.bits)
        key = struct.pack('<I', header)  # 32 bit key, little endian

        # Add variable length data
        try:
            if self.bits == 32:
                value = struct.pack("<I", self.value)
            elif self.bits == 16:
                value = struct.pack("<H", self.value)
            elif self.bits == 8:
                value = struct.pack("<B", self.value)
            elif self.bits == 1:
                value = struct.pack("<B", 0 if self.value == False else 1)
            elif self.bits == 64:
                value = struct.pack("<Q", self.value)
            else:
                raise ValueError
        except struct.error:
            raise ValueError

        data = key + value
        return data

    def unpack(self, data):
        """
        Unpacks configuration item key and data
        - Data length is dynamic and depends on key[30..28], invalid length raise ValueError

        @param data: bytearray to extract data from
        @return: number of bytes consumed
        """
        if len(data) < 4:
            raise ValueError

        results = struct.unpack('<I', data[:4])     # extract 32 bits in little endian mode
        key = results[0]
        data = data[4:]
        bytes_consumed = 4

        self.bits = CfgKeyData.bits_from_key(key)
        self.group_id = CfgKeyData.group_from_key(key)
        self.item_id = CfgKeyData.item_from_key(key)

        try:
            if self.bits == 32:
                results = struct.unpack("<I", data[:4])
                self.value = results[0]
                data = data[4:]
                bytes_consumed += 4
            elif self.bits == 16:
                results = struct.unpack("<H", data[:2])
                self.value = results[0]
                data = data[2:]
                bytes_consumed += 2
            elif self.bits == 8:
                results = struct.unpack("<B", data[:1])
                self.value = results[0]
                data = data[1:]
                bytes_consumed += 1
            elif self.bits == 1:
                results = struct.unpack("<B", data[:1])
                if results[0] == 0:
                    self.value = False
                elif results[0] == 1:
                    self.value = True
                else:
                    raise ValueError
                bytes_consumed += 1
            elif self.bits == 64:
                results = struct.unpack("<Q", data[:8])
                self.value = results[0]
                data = data[8:]
                bytes_consumed += 8
            else:
                raise ValueError
        except struct.error:
            raise ValueError

        return bytes_consumed

    def __str__(self):
        """
        Format a string of the form
        data1: key: CFG-TP-PULSE_DEF, bits: 8, value: 0 (0x00)
        """
        header = CfgKeyData.build_header(self.group_id, self.item_id, self.bits)
        key_name = UbxKeyId.to_str(header)

        res = self.name + ':'
        if key_name:
            res += f' key: {key_name}'
        else:
            res += f' group: 0x{self.group_id:02x}, item: 0x{self.item_id:03x}'

        res += f', bits: {self.bits}'
        if self.bits == 32:
            res += f', value: {self.value:d} (0x{self.value:08x})'
        elif self.bits == 16:
            res += f', value: {self.value:d} (0x{self.value:04x})'
        elif self.bits == 8:
            res += f', value: {self.value:d} (0x{self.value:02x})'
        elif self.bits == 1:
            str = "True" if self.value else "False"
            res += f', value: {str})'
        elif self.bits == 64:
            res += f', value: {self.value:d} (0x{self.value:016x})'
        else:
            raise ValueError
        return res
