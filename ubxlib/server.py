import binascii
import json
import logging
import queue
import socket
import sys
import threading
import time

from ubxlib.cid import UbxCID
from ubxlib.frame import UbxFrame
from ubxlib.frame_factory import FrameFactory
from ubxlib.parser import UbxParser
from ubxlib.ubx_ack import UbxAckAck, UbxAckNak

logger = logging.getLogger(__name__)


# TODO: Factor out code shared with server_tty.py and create baseclass
class GnssUBlox(threading.Thread):
    gpsd_control_socket = '/var/run/gpsd.sock'
    gpsd_data_socket = ('127.0.0.1', 2947)

    def __init__(self, device_name=None):
        super().__init__()

        self.device_name = device_name
        self.selected_device = None
        self.cmd_header = None
        self.connect_msg = f'?WATCH={{"enable":true,"raw":2}}'.encode()
        self.enabled = False

        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response_queue = queue.Queue()
        self.parser = UbxParser(self.response_queue)
        self.thread_ready_event = threading.Event()
        self.thread_stop_event = threading.Event()

        self.frame_factory = FrameFactory.getInstance()
        self.wait_cid = None
        self.gpsd_errors = 0
        self.cid_error = UbxCID(0x00, 0x01)

    def setup(self):
        # Register ACK-ACK frame, as it's used internally by this module
        self.frame_factory.register(UbxAckAck)
        self.frame_factory.register(UbxAckNak)

        # Start worker thread in daemon mode, will invoke run() method
        self.daemon = True
        self.start()

        # Wait for worker thread to become ready.
        # Without this wait we might send the command before the thread can
        # handle the response.
        logger.info('waiting for receive thread to become active')
        ready = self.thread_ready_event.wait(timeout=1.0)
        if not ready:
            logger.error('timeout while connecting to device')

        return ready

    def cleanup(self):
        logger.info('requesting thread to stop')
        self.thread_stop_event.set()

        # Wait until thread ended
        self.join(timeout=1.0)
        logger.info('thread stopped')

    def register_frame(self, frame_type):
        self.frame_factory.register(frame_type)

    def poll(self, message):
        """
        Poll a receiver status

        - sends the specified poll message
        - waits for receiver message with same class/id as poll message
        """
        assert isinstance(message, UbxFrame)

        self.expect(message.CID)
        self.send(message)
        res = self.wait()
        return self._check_poll(message, res)

    def set(self, message):
        """
        Send a set message to modem

        - creates bytes representation of set frame
        - send set message to modem
        - waits for ACK/NAK
        """
        assert isinstance(message, UbxFrame)

        message.pack()
        self.expect([UbxAckAck.CID, UbxAckNak.CID])
        self.send(message)
        res = self.wait()
        return self._check_ack_nak(message, res)

    """
    Private methods
    """
    def expect(self, cid):
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

    def send(self, ubx_message):
        # Must have connected
        assert self.selected_device

        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'sending {ubx_message}')
    
            # TODO: Keep socket connected all times?
            self.control_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.control_sock.connect(GnssUBlox.gpsd_control_socket)

            # sock.sendall('?devices'.encode())
            # data = sock.recv(512)
            # print(data.decode())

            # TODO: first call .pack()
            msg_in_binary = ubx_message.to_bytes()
            msg_in_ascii = binascii.hexlify(msg_in_binary)

            # TODO: move to outer function so it's not required to compute each time
            self.cmd_header = f'&{self.selected_device}='.encode()

            cmd = self.cmd_header + msg_in_ascii
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'sending control message {cmd}')

            self.control_sock.sendall(cmd)

            # checking for response (OK or ERROR)
            data = self.control_sock.recv(512)
            response = data.decode().strip()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'response: {response}')

            if 'ERROR' in response:
                self.gpsd_errors += 1
                logger.warning(f'command not accepted by gpsd, {self.gpsd_errors} error(s)')

                # Report error to waiting client, so it does not block
                # Use custom CID not used by u-blox, if there was someting
                # like UBX-ACK-TIMEOUT we would use that.
                # TODO: Consider UBX-ACK-NAK ..
                self.response_queue.put((self.cid_error, None))
            else:
                self.gpsd_errors = 0

            # TODO: check why we need to close socket here...
            self.control_sock.close()

        except socket.error as msg_in_ascii:
            logger.error(msg_in_ascii)

    def wait(self, timeout=3.0):
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

    def run(self):
        """
        Thread running method

        - receives raw data from gpsd
        - parses ubx frames, decodes them
        - if a frame is received it is put in the receive queue
        """
        # TODO: State machine with reconnect features?

        try:
            logger.info('connecting to gpsd')
            self.listen_sock.connect(('127.0.0.1', 2947))
            self.listen_sock.settimeout(0.25)
        except socket.error as msg:
            logger.error(msg)
            # TODO: Error handling

        try:
            logger.debug('starting raw listener on gpsd')
            self._enable()

            logger.debug('receiver ready')
            self.thread_ready_event.set()
            self._main_loop()

        except socket.error as msg:
            logger.error(msg)

        logger.debug('receiver done')

    def _main_loop(self):
        while not self.thread_stop_event.is_set():
            try:
                data = self.listen_sock.recv(8192)
                if data:
                    self.parser.process(data)
            except socket.timeout:
                pass

    def _enable(self):
        self.enabled = False
        self.listen_sock.send(self.connect_msg)
        while not self.enabled and not self.thread_stop_event.is_set():
            try:
                data = self.listen_sock.recv(8192)
                if data:
                    self._parse_gpsd_msg(data)
            except socket.timeout:
                pass

        logger.debug('connection established')

    def _parse_gpsd_msg(self, data):
        try:
            data_json = data.decode().splitlines()
            for entry in data_json:
                try:
                    data_map = json.loads(entry)
                    if 'class' in data_map:
                        msg_class = data_map['class']
                        if msg_class == 'VERSION':
                            self._parse_version(data_map)
                        elif msg_class == 'DEVICES':
                            self._parse_devices(data_map)
                except json.decoder.JSONDecodeError:
                    # Decoding error will happen if NMEA or other
                    # data is received here
                    pass

        except UnicodeDecodeError:
            # A decoding error will be thrown when binary data
            # e.g. ubx frames are received
            pass

    def _parse_version(self, data):
        logger.debug('checking gpsd version')
        release = data['release']
        logger.debug(f' release: {release}')

    def _parse_devices(self, data):
        logger.debug('checking available devices')

        for device in data['devices']:
            device_name = device['path']
            logger.debug(f' {device_name}')

            # If a device was requested, check for it ..
            if self.device_name:
                if self.device_name == device_name:
                    logger.debug(f'found desired device {device_name}')
                    self.selected_device = self.device_name
                    self.enabled = True
                    break
            # .. otherwise use first device listed
            else:
                logger.debug(f'using first found device {device_name}')
                self.selected_device = device_name
                self.enabled = True
                break

        if not self.enabled:
            logger.error('cannot connect to desired device')
