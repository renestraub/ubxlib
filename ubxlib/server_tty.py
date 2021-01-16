import logging
import time

from serial import Serial
from serial.serialutil import SerialException

from .parser_nmea import NmeaParser
from .parser_ubx import UbxParser
from .server_base import UbxServerBase_

logger = logging.getLogger(__name__)


class GnssUBlox(UbxServerBase_):
    def __init__(self, device_name, baudrate=115200):
        super().__init__()

        self.device_name = device_name
        self.baudrate = baudrate
        self.serial_port = Serial()

    def setup(self):
        res = super().setup()
        if res:
            res = self._open_port()
            return res

    def cleanup(self):
        self._close_port()
        super().cleanup()

    def set_baudrate(self, baud):
        # Making sure all data are sent before switching
        self.serial_port.flush()
        self.serial_port.baudrate = baud

    def scan(self, interval_in_s=1.500):
        """
        Scan for ubx or nmea frames

        The method returns True if at least two frames were decoded during the
        specified interval.

        Worst case scan interval has been empirically determined to 1.2 s
        """
        parser_ubx = UbxParser(None)
        parser_nmea = NmeaParser()

        ubx_frames = parser_ubx.frames_rx
        nmea_frames = parser_nmea.frames_rx

        self._flush_input()

        t_start = time.time()
        t_end = t_start + interval_in_s
        while time.time() < t_end:
            data = self._receive()
            if data:
                t_duration = time.time() - t_start

                parser_ubx.process(data)
                if parser_ubx.frames_rx - ubx_frames >= 2:
                    logger.info(f'ubx frames received within {t_duration:.3f} s')
                    return True

                parser_nmea.process(data)
                if parser_nmea.frames_rx - nmea_frames >= 2:
                    logger.info(f'nmea frames received within {t_duration:.3f} s')
                    return True

    """
    Base class implementation
    """
    def _recover(self):
        assert self.serial_port.is_open

        logger.warning("server_tty() performing recovery")

        # Recovery method for AM3352 problems
        # - Change bitrate while port is open
        #   This seems to reinitialize / fix a problem with MDR register
        # Reference:
        #   SPRZ360I AM335x Errata
        #   Advisory 1.0.35 - UART: Transactions to MDR1 Register May Cause Undesired Effect
        #                     on UART Operation
        current_br = self.serial_port.baudrate
        self.serial_port.baudrate = 9600
        self.serial_port.baudrate = current_br

    def _receive(self):
        assert self.serial_port.is_open

        # Read single bytes only, so that parser can stop at last byte
        # of a frame. When reading large blocks, read() blocks until timeout
        # when no (more) data arrives.
        # see _open_port() for read timeout
        data = self.serial_port.read(1)

        return data

    def _transmit(self, data):
        assert self.serial_port.is_open

        bytes_sent = self.serial_port.write(data)
        # if logger.isEnabledFor(logging.DEBUG):
        #     logger.debug(f"sent {bytes_sent} bytes")
        return bytes_sent == len(data)

    def _flush_input(self):
        assert self.serial_port.is_open

        self.serial_port.reset_input_buffer()

    """
    Private methods
    """
    def _open_port(self):
        self.serial_port.port = self.device_name
        self.serial_port.timeout = 0.1
        self.serial_port.xonxoff = False
        self.serial_port.dsrdtr = False
        self.serial_port.rtscts = False
        self.serial_port.exclusive = True

        try:
            self.serial_port.open()
            # Configure baudrate only after port has been opened.
            # Strange behavior on AM335x has been observed when baudrate
            # is configured before/with opening.
            # See _recover() for more details
            self.serial_port.baudrate = self.baudrate
            return self.serial_port.is_open
        except SerialException:
            # Can't open serial port, just fall through to return None
            pass

    def _close_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
