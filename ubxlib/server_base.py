import binascii
import logging
import time

from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.frame_factory import FrameFactory
from ubxlib.parser_ubx import UbxParser
from ubxlib.ubx_ack import UbxAckAck, UbxAckNak
from ubxlib.ubx_mga_ack_data0 import UbxMgaAckData0

logger = logging.getLogger(__name__)


class UbxServerBase_(object):
    def __init__(self):
        super().__init__()

        self.cid_crc_error = UbxCID(0x00, 0x02)
        self.parser = UbxParser(self.cid_crc_error)
        self.frame_factory = FrameFactory.getInstance()
        self.max_retries = 2
        self.retry_delay_in_ms = 1800

    def setup(self):
        # Register ACK-ACK/ACK-NAK frames, as they are used internally by this module
        self._register_response(UbxAckAck)
        self._register_response(UbxAckNak)

        # Register MGA-ACK-DATA0 so we can check result of MGA requests
        self._register_response(UbxMgaAckData0)
        return True

    def cleanup(self):
        self.frame_factory.destroy()
        self.frame_factory = None


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
        - if poll is for configuration frame
          - wait for ACK (or NAK) to poll request (note: ACK is sent after response)
        - retries in case no answer is received
        """
        assert isinstance(frame_poll, UbxFrame)
        logger.debug(f"polling {frame_poll.NAME}")

        # Determine class of response frame so we can properly decode the incoming answer
        # Currently we rely on frame factory concept. Type of frame is just registered
        # as formerly done by user of the library
        # TODO: Remove frame factory and decode frames in wait() method directly.
        response_class = frame_poll._cls_response()
        logger.debug(f'expecting response {response_class.NAME} {response_class.CID}')
        self._register_response(response_class)

        # In general we expect a response frame with the exact same CID.
        # If this is a configuration message, also check ACK frame,
        if frame_poll.CID.cls == UbxCID.CLASS_CFG:
            wait_cids = [frame_poll.CID, UbxAckAck.CID, UbxAckNak.CID]
        else:
            wait_cids = [frame_poll.CID]
        self.parser.set_filters(wait_cids)

        # Serialize polling frame payload.
        # Only a few polling frames required payload, most come w/o.
        frame_poll.pack()

        for retry in range(self.max_retries + 1):
            if retry != 0:
                logger.warning(f'poll: timeout, retrying {retry}')

            self._flush_input()
            res = self._send(frame_poll)

            if res:
                state = 'wait-response'
                response = None
                t_start = time.time()

                self.parser.empty_queue()
                self.parser.restart()

                while state != "ok" and state != 'timeout':
                    packet = self._wait()
                    if packet:
                        t_duration = time.time() - t_start
                        if state == 'wait-response':
                            check = self._check_poll(frame_poll, packet)
                            if check:
                                logger.debug(f'response received after {t_duration:.2f} s')
                                response = packet
                                if frame_poll.CID.cls == UbxCID.CLASS_CFG:
                                    # Only wait for ack if this is a CFG request ..
                                    state = 'wait-ack'
                                else:
                                    # .. otherwise we are done here
                                    state = 'ok'
                        elif state == 'wait-ack':
                            check = self._check_ack_nak(frame_poll, packet)
                            if check == 'ACK':
                                logger.debug(f'ACK received after {t_duration:.2f} s')
                                state = 'ok'
                            elif check == 'NAK':
                                # Not sure why we should ever get a NAK frame
                                logger.warning(f"NAK received\n{packet}")
                    else:
                        state = 'timeout'
                        break

                if state == 'ok':
                    assert response
                    return response
                else:
                    self._recover()
            else:
                logger.warning('poll: send failed')

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

        for retry in range(self.max_retries + 1):
            if retry != 0:
                logger.warning(f'set: timeout, retrying {retry}')

            self._flush_input()
            res = self._send(frame_set)
            if res:
                t_start = time.time()

                self.parser.empty_queue()
                self.parser.restart()

                packet = self._wait()
                if packet:
                    t_duration = time.time() - t_start
                    check = self._check_ack_nak(frame_set, packet)
                    if check == 'ACK':
                        logger.debug(f'ACK received after {t_duration:.2f} s')
                        return packet
                    elif check == 'NAK':
                        logger.debug(f'NAK received after {t_duration:.2f} s')
                        return packet
                else:
                    self._recover()
            else:
                logger.warning('set: send failed')

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

        for retry in range(self.max_retries + 1):
            if retry != 0:
                logger.warning(f'set_mga: timeout, retrying {retry}')

            self._flush_input()
            res = self._send(frame_set_mga)
            if res:
                t_start = time.time()

                self.parser.empty_queue()
                self.parser.restart()

                packet = self._wait()
                if packet:
                    t_duration = time.time() - t_start
                    check = self._check_mga(frame_set_mga, packet)
                    if check:
                        logger.debug(f'MGA-ACK received after {t_duration:.2f} s')
                        return packet
                else:
                    self._recover()
            else:
                logger.warning('set_mga: send failed')

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

        Occassionaly the communication fails with lots of checksum errors.
        The reason why erraneous frames are suddenly received is not clear.
        Usually one byte in a frame is just wrong, no bytes are missing or
        duplicated.

        Possible problems
         - Overload of receiver
         - UART driver problem <- likely
         - Physical interface problem

        Must be implemented by derived class.
        - i.e. close and reopen serial tty.
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
    def _register_response(self, frame_type):
        self.frame_factory.register(frame_type)

    def _send(self, ubx_message):
        """
        Send ubx frame to modem via backend driver
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'sending {ubx_message}')

        msg_in_binary = ubx_message.to_bytes()
        res = self._transmit(msg_in_binary)
        if not res:
            logger.warning('command could not be sent')

        return res

    def _wait(self):
        retry_delay_in_s = self.retry_delay_in_ms / 1000.0
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'waiting {retry_delay_in_s}s for response')

        # self.parser.empty_queue()
        # self.parser.restart()

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
