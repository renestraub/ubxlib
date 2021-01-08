import logging
from enum import Enum

logger = logging.getLogger(__name__)


class NmeaParser(object):
    """
    Parser that tries to read NMEA frames from arbitrary byte stream

    $GNRMC,155215.00,A,4719.13883,N,00758.44996,E,0.259,,171020,2.47,E,A*3E\r\n
    """
    class State(Enum):
        """ Parser states """
        WAIT_SYNC = 1
        DATA = 2
        CHKSUM1 = 3
        CHKSUM2 = 4
        LINEEND = 5

    def __init__(self):
        super().__init__()

        self.frames_rx = 0
        self.state = __class__.State.WAIT_SYNC
        self._reset()

    def restart(self):
        self.state = __class__.State.INIT

    def process(self, data):
        for d in data:
            char = chr(d)
            self._process_byte(char)

    def _process_byte(self, data):
        if data == '$':
            self._reset()
            self.state = __class__.State.DATA
        else:
            if self.state == __class__.State.WAIT_SYNC:
                self._state_wait_sync(data)
            elif self.state == __class__.State.DATA:
                self._state_data(data)
            elif self.state == __class__.State.CHKSUM1:
                self._state_checksum1(data)
            elif self.state == __class__.State.CHKSUM2:
                self._state_checksum2(data)
            elif self.state == __class__.State.LINEEND:
                self._state_lineend(data)

    def _state_wait_sync(self, d):
        if d == '$':
            self._reset()
            self.state = __class__.State.DATA

    def _state_data(self, d):
        if d == '*':
            self.state = __class__.State.CHKSUM1
        else:
            self.msg_data += d
            self.checksum_data ^= ord(d)

    def _state_checksum1(self, d):
        val = self._to_bin(d)
        if val != -1:
            self.checksum = val << 4
            self.state = __class__.State.CHKSUM2
        else:
            self.state = __class__.State.WAIT_SYNC

    def _state_checksum2(self, d):
        val = self._to_bin(d)
        if val != -1:
            self.checksum += val

            if self.checksum == self.checksum_data:
                self.frames_rx += 1
                logger.debug(f'{self.msg_data}')
            else:
                logger.warning('checksum error in frame, discarding')

            self.state = __class__.State.LINEEND
        else:
            self.state = __class__.State.WAIT_SYNC

    def _state_lineend(self, d):
        if d == '\n':
            self.state = __class__.State.WAIT_SYNC

    def _reset(self):
        self.msg_data = ''
        self.checksum = 0
        self.checksum_data = 0

    @staticmethod
    def _to_bin(data):
        if data in '0123456789abcdefABCDEF':
            return int(data, 16)
        else:
            logger.debug('invalid checksum character')
            return -1
