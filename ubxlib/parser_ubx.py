import binascii
import logging
from enum import Enum

from .checksum import Checksum
from .cid import UbxCID
from .frame import UbxFrame

logger = logging.getLogger(__name__)


class UbxParser(object):
    """
    Parser that tries to extract UBX frames from arbitrary byte streams

    Byte streams can also be NMEA or other frames. Unfortunately,
    u-blox frame header also appears in NMEA frames (e.g. version
    information). Such data will be detected by a checksum error

    TODO: Do more elaborate parsing to filter out such data in advance
    """

    """ Maximum message length supported """
    MAX_MESSAGE_LENGTH = 1000

    class State(Enum):
        """ Parser states """
        INIT = 1
        SYNC = 2
        CLASS = 3
        ID = 4
        LEN1 = 5
        LEN2 = 6
        DATA = 7
        CRC1 = 8
        CRC2 = 9

    def __init__(self, crc_error_cid):
        super().__init__()

        self.crc_error_cid = crc_error_cid
        self.rx_queue = list()
        self.wait_cids = None
        self.checksum = Checksum()
        self.frames_rx = 0
        self.state = __class__.State.INIT
        self._reset()

    def restart(self):
        self.state = __class__.State.INIT

    def set_filter(self, cid):
        assert isinstance(cid, UbxCID)
        self.wait_cids = [cid]  # Put single filter in list

    def set_filters(self, cids):
        assert isinstance(cids, list)
        self.wait_cids = cids

    def empty_queue(self):
        self.rx_queue.clear()

    def packet(self):
        # Returns (cid, data) or (None, None)
        try:
            return self.rx_queue.pop(0)
        except IndexError:
            # No more frames to de-queue
            return (None, None)

    def process(self, data):
        for d in data:
            self._process_byte(d)

    def _process_byte(self, data):
        if self.state == __class__.State.INIT:
            self._state_init(data)
        elif self.state == __class__.State.SYNC:
            self._state_sync(data)
        elif self.state == __class__.State.CLASS:
            self._state_class(data)
        elif self.state == __class__.State.ID:
            self._state_id(data)
        elif self.state == __class__.State.LEN1:
            self._state_len1(data)
        elif self.state == __class__.State.LEN2:
            self._state_len2(data)
        elif self.state == __class__.State.DATA:
            self._state_data(data)
        elif self.state == __class__.State.CRC1:
            self._state_crc1(data)
        elif self.state == __class__.State.CRC2:
            self._state_crc2(data)

    def _state_init(self, d):
        if d == UbxFrame.SYNC_1:
            self.state = __class__.State.SYNC

    def _state_sync(self, d):
        if d == UbxFrame.SYNC_2:
            self._reset()
            self.state = __class__.State.CLASS
        else:
            self.state = __class__.State.INIT

    def _state_class(self, d):
        # TODO: Could add check for SYNC_1, SYNC_2 here, as both are not valid classes or IDs
        self.msg_class = d
        self.checksum.add(d)
        self.state = __class__.State.ID

    def _state_id(self, d):
        self.msg_id = d
        self.checksum.add(d)
        self.state = __class__.State.LEN1

    def _state_len1(self, d):
        self.msg_len = d
        self.checksum.add(d)
        self.state = __class__.State.LEN2

    def _state_len2(self, d):
        self.msg_len = self.msg_len + (d * 256)
        self.checksum.add(d)

        if self.msg_len == 0:
            self.state = __class__.State.CRC1
        elif self.msg_len > __class__.MAX_MESSAGE_LENGTH:
            logger.warning(f'invalid msg len {self.msg_len}')
            self.state = __class__.State.INIT
        else:
            self.ofs = 0
            self.state = __class__.State.DATA

    def _state_data(self, d):
        self.msg_data.append(d)
        self.checksum.add(d)
        self.ofs += 1

        if self.ofs == self.msg_len:
            self.state = __class__.State.CRC1

    def _state_crc1(self, d):
        self.cka = d
        self.state = __class__.State.CRC2

    def _state_crc2(self, d):
        self.ckb = d

        # if checksum matches received checksum ..
        if self.checksum.matches(self.cka, self.ckb):
            self.frames_rx += 1

            # .. and frame passes filter ..
            cid = UbxCID(self.msg_class, self.msg_id)

            if self.wait_cids and cid in self.wait_cids:
                # .. queue packet (CID and data)
                packet = (cid, self.msg_data)
                self.rx_queue.append(packet)
            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'no match - dropping {cid}, {self.msg_len} bytes')
        else:
            logger.warning('checksum error in frame, discarding')
            logger.warning(f'{self.msg_class:02x} {self.msg_id:02x} {binascii.hexlify(self.msg_data)}')

            crc_error_message = (self.crc_error_cid, None)
            self.rx_queue.append(crc_error_message)

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
