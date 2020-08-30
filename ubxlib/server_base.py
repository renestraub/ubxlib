import binascii
import logging
import queue
import threading
import time

from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.frame_factory import FrameFactory
from ubxlib.parser import UbxParser
from ubxlib.ubx_ack import UbxAckAck, UbxAckNak

logger = logging.getLogger(__name__)


# TODO: Factor out code shared with server_tty.py and create baseclass
class UbxServerBase_(threading.Thread):
    def __init__(self):
        super().__init__()

        self.response_queue = queue.Queue()
        self.parser = UbxParser(self.response_queue)
        self.thread_ready_event = threading.Event()
        self.thread_stop_event = threading.Event()

        self.frame_factory = FrameFactory.getInstance()
        self.wait_cid = None
        self.cid_error = UbxCID(0x00, 0x01)

    def setup(self):
        # Register ACK-ACK/ACK-NAK frames, as they are used internally by this module
        self.frame_factory.register(UbxAckAck)
        self.frame_factory.register(UbxAckNak)

        # Start worker thread in daemon mode, will invoke derived class
        # run() method
        self.daemon = True
        self.start()

        # Wait for worker thread to become ready.
        # Without this wait we might send the command before the thread can
        # handle the response.
        # TODO: Check if wait time is ok even for extrmely loaded system
        logger.info('waiting for receive thread to become active')

        time_req = time.time()
        ready = self.thread_ready_event.wait(timeout=1.0)
        time_confirm = time.time()

        if ready:
            logger.info(f'thread became ready within {time_confirm-time_req:.3f}s')
        else:
            logger.error('timeout while connecting to device')

        return ready

    def cleanup(self):
        logger.info('requesting thread to stop')

        time_req = time.time()
        self.thread_stop_event.set()

        # Wait until thread ended
        # TODO: Check if wait time is ok even for extrmely loaded system
        self.join(timeout=1.0)
        time_confirm = time.time()

        logger.info(f'thread stopped in {time_confirm-time_req:.3f}s')

    def register_frame(self, frame_type):
        self.frame_factory.register(frame_type)

    def poll(self, message):
        """
        Poll a receiver status

        - sends the poll message
        - waits for receiver message with same class/id as poll message
        """
        assert isinstance(message, UbxFrame)

        self._expect(message.CID)
        message.pack()
        self._send(message)
        res = self._wait()
        return self._check_poll(message, res)

    def set(self, message):
        """
        Send a set message to modem and wait for acknowledge

        - creates bytes representation of set frame
        - sends set message to modem
        - waits for ACK/NAK
        """
        assert isinstance(message, UbxFrame)

        self._expect([UbxAckAck.CID, UbxAckNak.CID])
        message.pack()
        self._send(message)
        res = self._wait()
        return self._check_ack_nak(message, res)

    def send(self, message):
        """
        Send a set message to modem without waiting for a response

        This method is typically used for commands that are not ACKed, i.e.
        - cold start
        - change baudrate
        """
        assert isinstance(message, UbxFrame)

        message.pack()
        self._send(message)

    """
    Private methods
    """
    def run(self):
        """
        This method must be implemented by a derived backend implementation

        It shall run the receiver which checks for backend data and feeds them to
        the parser for processing -> self.parser.process(data)
        """
        raise NotImplementedError

    def _expect(self, cid):
        """
        Define message to wait for
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
        This method must be implemented by a derived backend implementation

        It shall send the frame to the modem. Typical operation is to convert
        the frame to a uxb message with UbxFrame::to_bytes().
        Then send the byte buffer using the backend device
        """
        raise NotImplementedError

    def _wait(self, timeout=3.0):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'waiting {timeout}s for reponse from listener thread')

        # TODO: Timeout loop required if we have queue.get() with timeout?
        time_end = time.time() + timeout
        while time.time() < time_end:
            try:
                cid, data = self.response_queue.get(True, timeout)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'got response {cid}')

                if cid == self.cid_error:
                    logger.warning('error response, no frame available')

                    self.parser.clear_filter()
                    return None

                # TODO: Required if parser already filters for us?
                elif cid in self.wait_cid:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f'received expected frame {cid}')

                    ff = FrameFactory.getInstance()
                    try:
                        frame = ff.build_with_data(cid, data)

                    except KeyError:
                        # If we can't parse the frame, return as is
                        logger.debug(f'frame not registered, cannot decode: {binascii.hexlify(data)}')
                        frame = UbxFrame()

                    self.parser.clear_filter()
                    return frame

            except queue.Empty:
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
        