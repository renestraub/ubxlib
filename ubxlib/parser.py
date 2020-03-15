import logging
from enum import Enum

from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.checksum import Checksum


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
        INIT = 1
        SYNC = 2
        CLASS = 3
        ID = 4
        LEN1 = 5
        LEN2 = 6
        DATA = 7
        CRC1 = 8
        CRC2 = 9

    def __init__(self, rx_queue):
        super().__init__()

        self.rx_queue = rx_queue
        self.checksum = Checksum()

        self._reset()
        self.state = __class__.State.INIT

    def process(self, data):
        for d in data:
            if self.state == __class__.State.INIT:
                if d == UbxFrame.SYNC_1:
                    self.state = __class__.State.SYNC

            elif self.state == __class__.State.SYNC:
                if d == UbxFrame.SYNC_2:
                    self._reset()
                    self.state = __class__.State.CLASS
                else:
                    self.state = __class__.State.INIT

            elif self.state == __class__.State.CLASS:
                self.msg_class = d
                self.checksum.add(d)
                self.state = __class__.State.ID

            elif self.state == __class__.State.ID:
                self.msg_id = d
                self.checksum.add(d)
                self.state = __class__.State.LEN1

            elif self.state == __class__.State.LEN1:
                self.msg_len = d
                self.checksum.add(d)
                self.state = __class__.State.LEN2

            elif self.state == __class__.State.LEN2:
                self.msg_len = self.msg_len + (d * 256)
                self.checksum.add(d)
                # TODO: Handle case with len = 0 -> goto CRC directly
                # TODO: Handle case with unreasonable size
                self.ofs = 0
                self.state = __class__.State.DATA

            elif self.state == __class__.State.DATA:
                self.msg_data.append(d)
                self.checksum.add(d)
                self.ofs += 1
                if self.ofs == self.msg_len:
                    self.state = __class__.State.CRC1

            elif self.state == __class__.State.CRC1:
                self.cka = d
                self.state = __class__.State.CRC2

            elif self.state == __class__.State.CRC2:
                self.ckb = d

                # if checksum matches received checksum put frame in receive queue
                if self.checksum.matches(self.cka, self.ckb):
                    # Send CID and data as tuple to server
                    self.rx_queue.put((UbxCID(self.msg_class, self.msg_id), self.msg_data))
                else:
                    logger.warning(f'checksum error in frame, discarding')

                self._reset()
                self.state = __class__.State.INIT

    def _reset(self):
        self.msg_class = 0
        self.msg_id = 0
        self.msg_len = 0
        self.msg_data = bytearray()
        self.cka = 0
        self.ckb = 0
        self.ofs = 0

        self.checksum.reset()
