import binascii
import json
import logging
import socket

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
        self.connect_msg = '?WATCH={"enable":true,"raw":2}'.encode()
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.enabled = False

    def setup(self):
        res = super().setup()
        self._open_port()
        self._enable()

        assert self.selected_device
        self.cmd_header = f'&{self.selected_device}='.encode()
        return res

    def cleanup(self):
        self.enabled = False
        self._close_port()
        super().cleanup()

    """
    Base class implementation
    """
    def _recover(self):
        # gpsd socket communication has shown to be stable
        # no recovery is required
        pass

    def _receive(self):
        # Check if there is data, forward to parser to process
        try:
            data = self.listen_sock.recv(128)
            if data:
                return data
        except socket.timeout:
            pass

    def _transmit(self, data):
        assert self.selected_device         # Must be connected

        success = False

        try:
            self.control_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.control_sock.connect(GnssUBlox.gpsd_control_socket)
            self.control_sock.settimeout(0.020)

            msg_in_ascii = binascii.hexlify(data)

            cmd = self.cmd_header + msg_in_ascii
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'sending control message {cmd}')

            self.control_sock.sendall(cmd)

            # checking for response (OK or ERROR)
            data = self.control_sock.recv(32)
            response = data.decode().strip()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'response: {response}')

            if 'OK' in response:
                success = True
            # else:
            #    logger.warning(f'command not accepted by gpsd')

            # TODO: Why does this small delay make code more reliable?
            # time.sleep(0.1)

            self.control_sock.shutdown(socket.SHUT_RDWR)
            self.control_sock.close()

        except socket.error as e:
            logger.error(e)

        return success

    """
    Private methods
    """
    def _open_port(self):
        try:
            self.listen_sock.connect(self.gpsd_data_socket)
            self.listen_sock.settimeout(0.25)
        except socket.error as msg:
            # TODO: Error handling
            logger.error(msg)

    def _close_port(self):
        if self.listen_sock:
            self.listen_sock.shutdown(socket.SHUT_RDWR)
            self.listen_sock.close()
            self.listen_sock = None

    def _enable(self):
        self.enabled = False
        self.listen_sock.send(self.connect_msg)

        # TODO: Timeout check for response!
        while not self.enabled:
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
