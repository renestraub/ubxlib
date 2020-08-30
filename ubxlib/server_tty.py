import binascii
import logging
import time

from serial import Serial
from serial.serialutil import SerialException

from ubxlib.server_base import UbxServerBase_

logger = logging.getLogger(__name__)


class GnssUBlox(UbxServerBase_):
    def __init__(self, device_name=None, baudrate=115200):
        super().__init__()

        self.device_name = device_name
        self.baudrate = baudrate
        self.enabled = False
        self.serial_port = None
        self.tx_errors = 0

    def run(self):
        """
        Thread running method

        - receives raw data from tty
        - parses ubx frames, decodes them
        - if a frame is received it is put in the receive queue
        """
        try:
            logger.info(f'connecting to {self.device_name} at {self.baudrate} bps')

            self.serial_port = Serial(self.device_name, timeout=0.1, baudrate=self.baudrate)
            assert self.serial_port

            self._main_loop()

            self.serial_port.close()
            self.serial_port = None

            logger.debug('receiver done')

        except SerialException as msg:
            logger.error(msg)

    def _send(self, ubx_message):
        assert self.enabled

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'sending {ubx_message}')

        msg_in_binary = ubx_message.to_bytes()

        # Send data to modem tty
        bytes_sent = self.serial_port.write(msg_in_binary)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"sent {bytes_sent} bytes")

        if bytes_sent != len(msg_in_binary):
            self.tx_errors += 1
            logger.warning(f'command not accepted by tty, {self.tx_errors} error(s)')

            # Report error to waiting client, so it does not block
            # Use custom CID not used by u-blox, if there was someting
            # like UBX-ACK-TIMEOUT we would use that.
            self.response_queue.put((self.cid_error, None))
        else:
            self.tx_errors = 0

    def _main_loop(self):
        logger.info('starting listener on tty')

        while not self.thread_stop_event.is_set():
            try:
                if not self.enabled:
                    self.enabled = True
                    self.thread_ready_event.set()

                # Intensive tests have shown that large read request perform better
                # in terms of data loss or TTY issues.
                data = self.serial_port.read(2048)
                if data:
                    self.parser.process(data)
            except SerialException as msg:
                logger.warning(msg)

        self.enabled = False


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
