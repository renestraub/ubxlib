import binascii
import logging
import queue
# import socket
import struct
# import sys
# import threading
import time
from enum import Enum

from ubxlib.frame import *


logger = logging.getLogger('gnss_tool')


class UbxParser(object):
    """
    Parser that tries to extract UBX frames from arbitrary byte streams

    Byte streams can also be NMEA or other frames. Unfortunately,
    u-blox frame header also appears in NMEA frames (e.g. version
    information). Such data will be detected by a checksum error

    TODO: Do more elaborate parsing to filter out such data in advance
    """

    class State(Enum):
        """
        Parser states
        """
        init = 1
        sync = 2
        cls = 3
        id = 4
        len1 = 5
        len2 = 6
        data = 7
        crc1 = 8
        crc2 = 9

    def __init__(self, rx_queue):
        super().__init__()

        self.rx_queue = rx_queue
        self.state = __class__.State.init

        self.msg_class = 0
        self.msg_id = 0
        self.msg_len = 0
        self.msg_data = bytearray()
        self.ofs = 0
        self.cka = 0
        self.ckb = 0

    def process(self, data):
        for d in data:
            if self.state == __class__.State.init:
                if d == UbxFrame.SYNC_1:
                    self.state = __class__.State.sync

            elif self.state == __class__.State.sync:
                if d == UbxFrame.SYNC_2:
                    self._reset()
                    self.state = __class__.State.cls
                else:
                    self.state = __class__.State.init

            elif self.state == __class__.State.cls:
                self.msg_class = d
                self.state = __class__.State.id

            elif self.state == __class__.State.id:
                self.msg_id = d
                self.state = __class__.State.len1

            elif self.state == __class__.State.len1:
                self.msg_len = d
                self.state = __class__.State.len2

            elif self.state == __class__.State.len2:
                self.msg_len = self.msg_len + (d * 256)
                # TODO: Handle case with len = 0 -> goto CRC directly
                # TODO: Handle case with unreasonable size
                self.ofs = 0
                self.state = __class__.State.data

            elif self.state == __class__.State.data:
                self.msg_data.append(d)
                self.ofs += 1
                if self.ofs == self.msg_len:
                    self.state = __class__.State.crc1

            elif self.state == __class__.State.crc1:
                self.cka = d
                self.state = __class__.State.crc2

            elif self.state == __class__.State.crc2:
                self.ckb = d

                # Build frame from received data. This computes the checksum
                # if checksum matches received checksum forward message to parser
                frame = UbxFrame(self.msg_class, self.msg_id, self.msg_len, self.msg_data)
                if frame.cka == self.cka and frame.ckb == self.ckb:
                    self.parse_frame(frame)
                else:
                    logger.warning(f'checksum error in frame')

                self._reset()
                self.state = __class__.State.init

    def parse_frame(self, ubx_frame):
        if ubx_frame.is_class_id(0x09, 0x14):
            # logger.debug(f'UBX-UPD-SOS: {binascii.hexlify(ubx_frame.to_bytes())}')
            frame = UbxUpdSos(ubx_frame)
        elif ubx_frame.is_class_id(0x06, 0x31):
            # logger.debug(f'UBX-CFG-TP5: {binascii.hexlify(ubx_frame.to_bytes())}')
            frame = UbxCfgTp5(ubx_frame)
        else:
            # If we can't parse the frame, return as is
            frame = ubx_frame

        self.rx_queue.put(frame)

    def _reset(self):
        self.msg_class = 0
        self.msg_id = 0
        self.msg_len = 0
        self.msg_data = bytearray()
        self.cka = 0
        self.ckb = 0
        self.ofs = 0
