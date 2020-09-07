import binascii
import logging
import queue
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

        self.response_queue = queue.Queue()
        self.parser = UbxParser(self.response_queue, self.cid_crc_error)

        self.frame_factory = FrameFactory.getInstance()
        self.wait_cid = None
        self.max_retries = 0

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

    def set_retries(self, num):
        assert 0 <= num <= 10
        self.max_retries = num

    def poll(self, message):
        """
        Poll a receiver status

        - sends the poll message
        - waits for receiver message with same class/id as poll message
        - retries in case no answer is received
        """
        assert isinstance(message, UbxFrame)

        message.pack()
        self._expect(message.CID)

        for tries in range(self.max_retries+1):
            if tries > 0:
                logger.warning(f'poll failed, retrying attempt {tries}')

            res = self._send(message)
            if res:
                res = self._wait()
                res_check = self._check_poll(message, res)
                if res_check:
                    self._calm()
                    return res_check
            else:
                logger.warning('send failed')

            # Give receiver time to recover
            time.sleep(tries*0.5)

            # It seems we can't recover from an error here
            # so ask derived class to perform recovery actions
            self._recover()

        self._calm()

        # TODO:
        # If we get here something truly bad is going on.
        # Typically the logs show a lot of checksum errors. 
        # It is not clear whether these are real or if we just
        # loose data. 
        # Sometimes even Linux driver errors are visible in the 
        # kernel log 
        assert False

    def set(self, message):
        """
        Send a set message to modem and wait for acknowledge

        - creates bytes representation of set frame
        - sends set message to modem
        - waits for ACK/NAK
        """
        assert isinstance(message, UbxFrame)

        message.pack()

        self._expect([UbxAckAck.CID, UbxAckNak.CID])
        # TODO: Error handling/retry
        self._send(message)
        res = self._wait()
        self._calm()

        return self._check_ack_nak(message, res)

    def set_mga(self, message):
        """
        Send an MGA set message to modem and wait for acknowledge

        Note: MGA acknowledge must be enabled via CFG-NAVX5 to use this
        method.

        - creates bytes representation of set frame
        - sends set message to modem
        - waits for ACK-MGA-DATA0
        """
        assert isinstance(message, UbxFrame)
        assert message.CID.cls == 0x13      # TODO: Not best style to hardcode 0x13 for MGA Class

        message.pack()

        self._expect(UbxMgaAckData0.CID)
        # TODO: Error handling/retry
        self._send(message)
        res = self._wait()
        self._calm()

        return self._check_mga(message, res)

    def send(self, message):
        """
        Send a set message to modem without waiting for a response
        (fire and forget)

        This method is typically used for commands that are not ACKed, i.e.
        - cold start
        - change baudrate
        """
        assert isinstance(message, UbxFrame)

        message.pack()
        self._send(message)

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

    """
    Private methods
    """
    def _expect(self, cid):
        """
        Define messages to wait for

        Can be a single CID or a list of CIDs
        """
        if not isinstance(cid, list):
            cid = [cid]

        self.wait_cid = cid
        if logger.isEnabledFor(logging.DEBUG):
            for cid in self.wait_cid:
                logger.debug(f'expecting {cid}')

        self.parser.set_filter(self.wait_cid)

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

    def _calm(self):
        """
        Calm receiver so that no more frames are forwarded
        """
        self.parser.clear_filter()

    def _wait(self, timeout=3.0):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'waiting {timeout}s for response from listener thread')

        time_end = time.time() + timeout
        while time.time() < time_end:
            data = self._receive()
            if data:
                # process() places all decoded frames in response_queue
                self.parser.process(data)

            # Check if process could decode one or more frames
            # Loop exists when no more frames are to handle
            while True:
                try:
                    # cid, data = self.response_queue.get(True, timeout)
                    # Poll queue, no timeout, raises queue.Empty if there is nothing to read
                    cid, data = self.response_queue.get(True, False)

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f'got response {cid}')

                    if cid == self.cid_crc_error:
                        logger.warning("crc error, initiating recovery sequence")
                        self._recover()

                    # TODO: Required if parser already filters for us?
                    elif cid in self.wait_cid:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f'received expected frame {cid}')

                        ff = FrameFactory.getInstance()
                        try:
                            frame = ff.build_with_data(cid, data)
                            return frame
                        except KeyError:
                            # We can't parse the frame, is it registered()
                            logger.debug(f'frame not registered, cannot decode: {binascii.hexlify(data)}')
                    else:
                        # TODO: must never happen if filter works properly
                        logger.error(cid)
                        assert False

                except queue.Empty:
                    break

        logger.warning('timeout...')

    def _check_poll(self, request, res):
        if res:
            if res.CID == request.CID:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('response matches request')
                return res
            else:
                # Must never happen, as one request is in expected list
                logger.error(f'invalid frame received {res.CID}')
                assert False

    def _check_ack_nak(self, request, res):
        if res:
            if res.CID == UbxAckAck.CID:
                ack_cid = UbxCID(res.f.clsId, res.f.msgId)
                if ack_cid == request.CID:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug('ACK matches request')
                    return res
                else:
                    logger.warning(f'ACK {ack_cid} does not match request {request.CID}')
            elif res.CID == UbxAckNak.CID:
                logger.warning(f'request {request.CID} rejected, NAK received')
            else:
                # Must never happen. Only ACK/NAK in expected list
                logger.error(f'invalid frame received {res.CID}')
                assert False

    def _check_mga(self, request, res):
        if res:
            if res.CID == UbxMgaAckData0.CID:
                if res.f.type == 1:
                    return True
                else:
                    logger.warning(f'MGA message not accepted, error code {res.f.infoCode}')
            else:
                # Must never happen. Only MGA ACK in expected list
                logger.error(f'invalid frame received {res.CID}')
                assert False
