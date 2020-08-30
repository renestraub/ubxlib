import binascii
import json
import logging
import socket
import time

from ubxlib.server_base import UbxServerBase_

logger = logging.getLogger(__name__)


class GnssUBlox(UbxServerBase_):
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
        self.gpsd_errors = 0

    def run(self):
        """
        Thread running method

        - receives raw data from gpsd
        - parses ubx frames, decodes them
        - if a frame is received it is put in the receive queue
        """
        # TODO: State machine with reconnect features?

        logger.info('connecting to gpsd')

        try:
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

    def _send(self, ubx_message):
        # Must have connected
        assert self.selected_device

        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'sending {ubx_message}')
    
            # TODO: Keep socket connected all times?
            self.control_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.control_sock.connect(GnssUBlox.gpsd_control_socket)

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
                self.response_queue.put((self.cid_error, None))
            else:
                self.gpsd_errors = 0

            # TODO: check why we need to close socket here...
            self.control_sock.close()

        except socket.error as msg_in_ascii:
            logger.error(msg_in_ascii)

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
