import binascii
import logging
import time

from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.frame_factory import FrameFactory
from ubxlib.parser import UbxParser
from ubxlib.ubx_ack import UbxAckAck, UbxAckNak
from ubxlib.ubx_mga_ack_data0 import UbxMgaAckData0

logger = logging.getLogger(__name__)


class UbxServerBase_(object):
    def __init__(self):
        super().__init__()

        self.cid_crc_error = UbxCID(0x00, 0x02)
        self.parser = UbxParser(self.cid_crc_error)
        self.frame_factory = FrameFactory.getInstance()
        self.wait_cid = None
        self.max_retries = 2
        self.retry_delay_in_ms = 1800

    def setup(self):
        # Register ACK-ACK/ACK-NAK frames, as they are used internally by this module
        self.frame_factory.register(UbxAckAck)
        self.frame_factory.register(UbxAckNak)

        # Register MGA-ACK-DATA0 so we can check result of MGA requests
        self.frame_factory.register(UbxMgaAckData0)

        return True

    def cleanup(self):
        self.frame_factory.destroy()
        self.frame_factory = None

    def register_frame(self, frame_type):
        self.frame_factory.register(frame_type)

    def set_retries(self, retries):
        logger.debug(f"setting max retries to {retries}")
        assert 0 <= retries <= 10
        current = self.max_retries
        self.max_retries = retries
        return current

    def set_retry_delay(self, delay):
        logger.debug(f"setting retry delay to {delay} ms")
        assert 0 <= delay <= 5000
        current = self.retry_delay_in_ms
        self.retry_delay_in_ms = delay
        return current

    def poll(self, frame_poll):
        """
        Poll a receiver status

        - sends the poll message
        - waits for receiver message with same class/id as poll message
        - retries in case no answer is received
        """
        assert isinstance(frame_poll, UbxFrame)
        logger.debug(f"polling {frame_poll.NAME}")

        # We expect a response frame with the exact same CID
        wait_cid = frame_poll.CID
        self.parser.set_filter(wait_cid)

        # Serialize polling frame payload.
        # Only a few polling frames required payload, most come w/o.
        frame_poll.pack()

        t_start = time.time()

        for retry in range(self.max_retries + 1):
            self._flush_input()
            res = self._send(frame_poll)

            if res:
                packet = self._wait()
                if packet:
                    res_check = self._check_poll(frame_poll, packet)
                    if res_check:
                        t_stop = time.time()
                        logger.debug(f'response received after {(t_stop - t_start):.2f} s')
                        return packet
            else:
                logger.warning('send failed')

            logger.warning(f'poll: timeout, retrying {retry + 1}')
            self._recover()

        # TODO:
        # If we get here something truly bad is going on.
        # Typically the logs show a lot of checksum errors.
        # It is not clear whether these are real or if we just
        # loose data.
        # Sometimes even Linux driver errors are visible in the
        # kernel log

    def set(self, frame_set):
        """
        Send a set message to modem and wait for acknowledge

        - creates bytes representation of set frame
        - sends set message to modem
        - waits for ACK/NAK
        """
        assert isinstance(frame_set, UbxFrame)
        logger.debug(f"setting {frame_set.NAME}")

        # Wait for ACK-ACK / ACK-NAK
        self.parser.set_filters([UbxAckAck.CID, UbxAckNak.CID])

        # Get frame data (header, cls, id, len, payload, checksum a/b)
        frame_set.pack()

        t_start = time.time()

        for retry in range(self.max_retries + 1):
            self._flush_input()
            self._send(frame_set)

            packet = self._wait()
            if packet:
                res_check = self._check_ack_nak(frame_set, packet)
                if res_check == 'ACK':
                    t_stop = time.time()
                    logger.debug(f'ACK received after {(t_stop - t_start):.2f} s')
                    return packet
                elif res_check == 'NAK':
                    t_stop = time.time()
                    logger.debug(f'NAK received after {(t_stop - t_start):.2f} s')
                    return packet

            logger.warning(f'set: timeout, retrying {retry + 1}')
            self._recover()

    def set_mga(self, frame_set_mga):
        """
        Send an MGA set message to modem and wait for acknowledge

        Note: MGA acknowledge must be enabled via CFG-NAVX5 to use this
        method.

        - creates bytes representation of set frame
        - sends set message to modem
        - waits for ACK-MGA-DATA0
        """
        assert isinstance(frame_set_mga, UbxFrame)
        assert frame_set_mga.CID.cls == 0x13      # TODO: Not best style to hardcode 0x13 for MGA Class
        logger.debug(f"setting mga {frame_set_mga.NAME}")

        # Wait for special MGA ACK frame
        self.parser.set_filter(UbxMgaAckData0.CID)

        # Get frame data (header, cls, id, len, payload, checksum a/b)
        frame_set_mga.pack()

        # TODO: Error handling/retry
        self._flush_input()
        self._send(frame_set_mga)

        packet = self._wait()
        if packet:
            res_check = self._check_mga(frame_set_mga, packet)
            if res_check:
                return packet

    def fire_and_forget(self, frame_set):
        """
        Send a set message to modem without waiting for a response
        (fire and forget)

        This method is typically used for commands that are not ACKed, i.e.
        - cold start
        - change baudrate
        """
        assert isinstance(frame_set, UbxFrame)
        logger.debug(f"firing {frame_set.NAME}")

        frame_set.pack()
        self._send(frame_set)

    @DeprecationWarning
    def send(self, message):
        self.fire_and_forget(message)

    """
    Overrides to be provided by backend implementation
    """
    def _recover(self):
        """
        Perform actions required to recover communication link.

        I.e. close and reopen serial tty.
        Must be implemented by derived class.
        """
        raise NotImplementedError

    def _receive(self):
        """
        This method must be implemented by a derived backend implementation

        It shall try to receive data from the modem. Any data received shall
        be returned. In case no data could be read, return None.

        Maximum runtime of this function is expected to be 100 ms so that
        incoming data is moved to processing stage quickly.
        """
        raise NotImplementedError

    def _transmit(self, data):
        """
        This method must be implemented by a derived backend implementation

        It shall send the frame to the modem. Typical operation is to convert
        the frame to a uxb message with UbxFrame::to_bytes().
        Then send the byte buffer using the backend device

        In case of success True shall be returned, False otherwise
        """
        raise NotImplementedError

    def _flush_input(self):
        """
        This method can be implemented by a derived backend

        If implemented, it shall flush all pending data in the input/receive
        queue.
        """
        pass

    """
    Private methods
    """
    def _send(self, ubx_message):
        """
        Send ubx frame to modem via backend driver
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'sending {ubx_message}')

        msg_in_binary = ubx_message.to_bytes()
        res = self._transmit(msg_in_binary)
        if not res:
            logger.warning(f'command could not be sent')

        return res

    def _wait(self):
        retry_delay_in_s = self.retry_delay_in_ms / 1000.0
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'waiting {retry_delay_in_s}s for response')

        self.parser.empty_queue()
        self.parser.restart()

        time_end = time.time() + retry_delay_in_s
        while time.time() < time_end:
            data = self._receive()
            if data:
                # process() places all decoded frames in rx queue
                self.parser.process(data)

            # Check if process could decode one or more frames
            # Loop exists when no more frames are to handle
            cid, data = self.parser.packet()
            if cid:
                if cid != self.cid_crc_error:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f'received expected frame {cid}')

                    ff = FrameFactory.getInstance()
                    try:
                        frame = ff.build_with_data(cid, data)
                        return frame
                    except KeyError:
                        # We can't parse the frame, is it registered()
                        logger.warning(f'frame not registered, cannot decode: {binascii.hexlify(data)}')
                else:
                    logger.warning("checksum error in frame, discarding")

        logger.warning('timeout...')

    def _check_poll(self, request, res):
        """ Check if response is for requested frame """
        if res.CID == request.CID:
            # if logger.isEnabledFor(logging.DEBUG):
            #     logger.debug('response matches request')
            return True
        else:
            # Must never happen, as only request CID is in expected list
            logger.warning(f'invalid frame received {res.CID}')

    def _check_ack_nak(self, request, res):
        if res.CID == UbxAckAck.CID:
            ack_cid = UbxCID(res.f.clsId, res.f.msgId)
            if ack_cid == request.CID:
                # if logger.isEnabledFor(logging.DEBUG):
                #     logger.debug('ACK matches request')
                return "ACK"
            else:
                # ACK is for another request
                logger.warning(f'ACK {ack_cid} does not match request {request.CID}')
        elif res.CID == UbxAckNak.CID:
            logger.warning(f'request {request.CID} rejected, NAK received')
            return "NAK"
        else:
            # Must never happen. Only ACK/NAK in expected list
            logger.error(f'invalid frame received {res.CID}')

    def _check_mga(self, request, res):
        if res.CID == UbxMgaAckData0.CID:
            if res.f.type == 1:
                return True
            else:
                logger.warning(f'MGA message not accepted, error code {res.f.infoCode}')
        else:
            # Must never happen. Only MGA ACK in expected list
            logger.error(f'invalid frame received {res.CID}')
