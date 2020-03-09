# import binascii
import logging
import struct

from ubxlib.checksum import Checksum


logger = logging.getLogger('gnss_tool')


class UbxFrame(object):
    CLASS = -1
    ID = -1

    SYNC_1 = 0xb5
    SYNC_2 = 0x62

    @classmethod
    def CLASS_ID(cls):
        return cls.CLASS, cls.ID

    def __init__(self, cls, id, data=bytearray()):
        super().__init__()
        self.cls = cls
        self.id = id
        self.data = data
        self.length = len(self.data)

        self.checksum = Checksum()

    def is_class_id(self, cls, id):
        return cls == self.cls and id == self.id

    def to_bytes(self):
        self._calc_checksum()

        msg = bytearray([UbxFrame.SYNC_1, UbxFrame.SYNC_2])
        msg.append(self.cls)
        msg.append(self.id)
        msg.append((self.length >> 0) % 0xFF)
        msg.append((self.length >> 8) % 0xFF)
        msg += self.data
        msg.append(self.cka)
        msg.append(self.ckb)

        return msg

    def _calc_checksum(self):
        self.checksum.reset()

        self.checksum.add(self.cls)
        self.checksum.add(self.id)
        self.checksum.add((self.length >> 0) & 0xFF)
        self.checksum.add((self.length >> 8) & 0xFF)

        for d in self.data:
            self.checksum.add(d)

        self.cka, self.ckb = self.checksum.value()

    def __str__(self):
        return f'UBX: cls:{self.cls:02x} id:{self.id:02x} len:{self.length}'


class UbxPoll(UbxFrame):
    """
    Base class for a polling frame.

    Create by specifying u-blox message class and id.
    """
    def __init__(self):
        super().__init__(self.CLASS, self.ID)


class UbxUpdSosPoll(UbxPoll):
    CLASS = 0x09
    ID = 0x14

    def __init__(self):
        super().__init__()


class UbxUpdSos(UbxFrame):
    CLASS = 0x09
    ID = 0x14

    def __init__(self, msg):
        super().__init__(msg.cls, msg.id, msg.data)
        if msg.length == 8 and msg.data[0] == 3:
            self.cmd = msg.data[0]
            self.response = msg.data[4]
        else:
            self.cmd = -1
            self.response = -1

    def __str__(self):
        return f'UBX-UPD-SOS: cmd:{self.cmd}, response:{self.response}'


class UbxUpdSosAction(UbxFrame):
    CLASS = 0x09
    ID = 0x14

    # msg_upd_sos_save = bytearray.fromhex('09 14 04 00 00 00 00 00')
    # msg_upd_sos_clear = bytearray.fromhex('09 14 04 00 01 00 00 00')
    def __init__(self, action):
        msg = bytearray.fromhex('01 00 00 00')
        super().__init__(self.CLASS, self.ID, msg)


class UbxCfgTp5Poll(UbxPoll):
    CLASS = 0x06
    ID = 0x31

    def __init__(self):
        super().__init__()


class UbxCfgTp5(UbxFrame):
    CLASS = 0x06
    ID = 0x31

    def __init__(self, msg):
        super().__init__(msg.cls, msg.id, msg.data)
        if msg.length == 32:
            tpIdx, version, res1, antCableDelay, rfGroupDelay = struct.unpack('BBhhh', msg.data[0:8])
            print(tpIdx, version, antCableDelay, rfGroupDelay)

            freqPeriod, freqPeriodLock, pulseLenRatio, pulseLenRatioLock = struct.unpack('<IIII', msg.data[8:24])
            print(freqPeriod, freqPeriodLock, pulseLenRatio, pulseLenRatioLock)

            userConfigDelay = struct.unpack('<I', msg.data[24:28])
            print(userConfigDelay)

            flags = struct.unpack('<I', msg.data[24:28])
            print(flags)
        else:
            pass

    def __str__(self):
        return f'UBX-CFG-TP5: ...'
