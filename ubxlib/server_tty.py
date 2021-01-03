# import binascii
import logging

from serial import Serial
from serial.serialutil import SerialException

from ubxlib.server_base import UbxServerBase_

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
        self.serial_port.baudrate = baud

    """
    Base class implementation
    """
    def _recover(self):
        assert self.serial_port.is_open

        logger.warning("server_tty() perfoming recovery")

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

        # Read single bytes only, so that parser can stop at least byte
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
        self.serial_port.baudrate = self.baudrate
        self.serial_port.timeout = 0.1
        self.serial_port.xonxoff = False
        self.serial_port.dsrdtr = False
        self.serial_port.rtscts = False

        try:
            self.serial_port.open()
            return self.serial_port.is_open
        except SerialException:
            # Can't open serial port, just fall through to return None
            pass

    def _close_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()


class GnssUBloxBitrate:
    def __init__(self, device_name=None):
        super().__init__()

        self.device_name = device_name
        self.baudrate = None

    def determine(self):
        """
        Determine current baudrate of GNSS modem

        Theory of operation:
        - set well known bitrate and check whether data can be received
        - this assumes the modem is transmitting ubx or NMEA frames
        """
        bitrates_to_check = [115200, 9600]
        self.baudrate = None

        for b in bitrates_to_check:
            logger.info(f'checking bitrate {b}')
            ser = Serial(self.device_name, timeout=0.1, baudrate=b)
            ser.reset_input_buffer()

            data_bin = bytes()
            data_ascii = ''

            # Without further configuration a set of data is sent once per second.
            # 15 loops with a 0.1 sec read timeout is therefore enough for a decision
            for _ in range(15):
                data = ser.read(1024)

                # Just add new data to binary buffer
                data_bin += data

                # For ASCII its a bit more complicated, we need to decode the bytes
                # buffer from ser.read()
                # If binary data or dummy bytes are received this will lead to a
                # Unicode conversion error we have to catch.
                try:
                    ascii_str = data.decode()
                    # We only get here if ascii_str is valid, we can the add it to
                    # the ascii data stream. If there is a conversion error the
                    # new data is dropped
                    data_ascii += ascii_str
                except UnicodeError:
                    logger.debug("unicode conversion issue, dropping buffer")

                # if logger.isEnabledFor(logging.DEBUG):
                #     logger.debug(f'bin: {binascii.hexlify(data_bin)}, ascii: {data_ascii}')

                # Check for NMEA frames (ASCII)
                if 'GGA,' in data_ascii or 'GSV,' in data_ascii or 'GGL,' in data_ascii or 'RMC,' in data_ascii:
                    logger.info('nmea sentence detected')
                    self.baudrate = b
                    break
                # Check for ubx frames
                elif bytes.fromhex('B562') in data_bin:
                    logger.info('ubx frame detected')
                    self.baudrate = b
                    break

            ser.close()
            ser = None

            if self.baudrate:
                logger.info(f"current bitrate of GNSS is {b}")
                return b

        # If we get here, we couldn't find the bitrate
        return None
