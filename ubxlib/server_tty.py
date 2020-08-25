import binascii
import logging
import queue
import sys
import threading
import time

from serial import Serial
from serial.serialutil import SerialException

from ubxlib.frame_factory import FrameFactory
from ubxlib.frame import UbxFrame, UbxCID
from ubxlib.ubx_ack import UbxAckAck
from ubxlib.parser import UbxParser


logger = logging.getLogger('gnss_tool')

# TODO: Factor out code shared with server.py and create baseclass
class GnssUBlox(threading.Thread):
    def __init__(self, device_name=None, baudrate=115200):
        super().__init__()

        self.device_name = device_name
        self.baudrate = baudrate
        self.enabled = False

        self.serial_port = None
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
        return res

    def set(self, message):
        """
        Send a set message to modem

        - creates bytes representation of set frame
        - send set message to modem
        - waits for ACK
        """
        assert isinstance(message, UbxFrame)

        self.expect(UbxAckAck.CID)
        message.pack()
        self.send(message)
        res = self.wait()

        return res

    def expect(self, cid):
        """
        Define message message to wait for
        """
        logger.debug(f'expecting {cid}')
        self.wait_cid = cid
        self.parser.set_filter(cid)

    def send(self, ubx_message):
        assert self.enabled

        logger.debug(f'sending {ubx_message}')

        # TODO: first call .pack()
        msg_in_binary = ubx_message.to_bytes()
        # logger.debug(f'sending {msg_in_binary}')

        # Send frame to modem tty
        bytes_sent = self.serial_port.write(msg_in_binary)
        logger.debug(f"sent {bytes_sent} bytes")

        if bytes_sent != len(msg_in_binary):
            self.gpsd_errors += 1
            logger.warning(f'command not accepted by tty, {self.gpsd_errors} error(s)')

            # Report error to waiting client, so it does not block
            # Use custom CID not used by u-blox, if there was someting
            # like UBX-ACK-TIMEOUT we would use that.
            # TODO: Consider UBX-ACK-NAK ..
            self.response_queue.put((self.cid_error, None))
        else:
            self.gpsd_errors = 0

    def wait(self, timeout=3.0):
        logger.debug(f'waiting {timeout}s for reponse from listener thread')

        # TODO: Timeout loop required if we have queue.get() with timeout?
        time_end = time.time() + timeout
        while time.time() < time_end:
            try:
                cid, data = self.response_queue.get(True, timeout)
                logger.debug(f'got response {cid}')

                if cid == self.cid_error:
                    logger.warning('error response, no frame available')

                    self.parser.clear_filter()
                    return None

                # TODO; Required if parser already filters for us?
                elif cid == self.wait_cid:
                    logger.debug(f'received expected frame {cid}')

                    ff = FrameFactory.getInstance()
                    try:
                        frame = ff.build_with_data(cid, data)

                    except KeyError:
                        # If we can't parse the frame, return as is
                        logger.debug(f'default: {binascii.hexlify(data)}')
                        frame = UbxFrame()

                    self.parser.clear_filter()
                    return frame

            except queue.Empty:
                logger.warning('timeout...')

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

            logger.debug('starting listener on tty')
            self.thread_ready_event.set()
            self._main_loop()

            logger.debug('receiver done')

        except SerialException as msg:
            logger.error(msg)

    def _main_loop(self):
        self.enabled = True
        while not self.thread_stop_event.is_set():
            try:
                data = self.serial_port.read(1024)
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

                logger.debug(f'bin: {binascii.hexlify(data_bin)}, ascii: {data_ascii}')

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

            if self.baudrate:
                logger.info(f"current bitrate of GNSS is {b}")
                return b

        # If we get here, we couldn't find the bitrate
        return None
