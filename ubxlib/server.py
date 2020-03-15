import binascii
import logging
import queue
import socket
import sys
import threading
import time

from ubxlib.frame import UbxFrame
from ubxlib.ubx_ack import UbxAckAck
from ubxlib.ubx_cfg_tp5 import UbxCfgTp5
from ubxlib.ubx_upd_sos import UbxUpdSos
from ubxlib.parser import UbxParser


logger = logging.getLogger('gnss_tool')


class GnssUBlox(threading.Thread):
    gpsd_control_socket = '/var/run/gpsd.sock'
    gpsd_data_socket = ('127.0.0.1', 2947)

    def __init__(self, device_name):
        super().__init__()

        self.device_name = device_name
        self.cmd_header = f'&{self.device_name}='.encode()
        self.connect_msg = f'?WATCH={{"device":"{self.device_name}","enable":true,"raw":2}}'.encode()

        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response_queue = queue.Queue()
        self.parser = UbxParser(self.response_queue)
        self.thread_ready_event = threading.Event()
        self.thread_stop_event = threading.Event()

        self.wait_msg_class = -1
        self.wait_msg_id = -1

    def setup(self):
        # Start worker thread in daemon mode, will invoke run() method
        self.daemon = True
        self.start()

        # Wait for worker thread to become ready.
        # Without this wait we might send the command before the thread can
        # handle the response.
        logger.info('waiting for receive thread to become active')
        self.thread_ready_event.wait()

    def cleanup(self):
        logger.info('requesting thread to stop')
        self.thread_stop_event.set()

        # Wait until thread ended
        self.join(timeout=1.0)
        logger.info('thread stopped')

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

    def expect(self, cid):
        """
        Define message message to wait for
        """
        logger.debug(f'expecting {cid}')
        self.wait_cid = cid

    def send(self, ubx_message):
        try:
            logger.debug(f'sending {ubx_message}')

            self.control_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.control_sock.connect(GnssUBlox.gpsd_control_socket)

            # sock.sendall('?devices'.encode())
            # data = sock.recv(512)
            # print(data.decode())

            # TODO: first call .pack()
            msg_in_binary = ubx_message.to_bytes()
            msg_in_ascii = binascii.hexlify(msg_in_binary)
            # logger.debug(f'sending {msg_in_ascii}')

            cmd = self.cmd_header + msg_in_ascii
            logger.debug(f'sending control message {cmd}')
            self.control_sock.sendall(cmd)

            # checking for response (OK or ERROR)
            data = self.control_sock.recv(512)
            response = data.decode().strip()
            logger.debug(f'response: {response}')

            # TODO: check why we need to close socket here...
            self.control_sock.close()

        except socket.error as msg_in_ascii:
            logger.error(msg_in_ascii)

    def wait(self, timeout=3.0):
        logger.debug(f'waiting {timeout}s for reponse from listener thread')

        time_end = time.time() + timeout
        while time.time() < time_end:
            try:
                cid, data = self.response_queue.get(True, timeout)
                logger.debug(f'got response {cid}')

                if cid == self.wait_cid:
                    logger.debug(f'received expected frame {cid}')

                    # TODO: Frame Factory
                    if UbxAckAck.MATCHES(cid):
                        # logger.debug(f'UBX-CFG-TP5: {binascii.hexlify(data)}')
                        frame = UbxAckAck.construct(data)
                        print(frame)
                    elif UbxUpdSos.MATCHES(cid):
                        logger.debug(f'UBX-UPD-SOS: {binascii.hexlify(data)}')
                        frame = UbxUpdSos.construct(data)
                    elif UbxCfgTp5.MATCHES(cid):
                        # logger.debug(f'UBX-CFG-TP5: {binascii.hexlify(data)}')
                        frame = UbxCfgTp5.construct(data)
                    else:
                        # If we can't parse the frame, return as is
                        logger.debug(f'default: {binascii.hexlify(data)}')
                        frame = UbxFrame()  #.construct(data)

                    return frame

            except queue.Empty:
                logger.warning('timeout...')

    def run(self):
        """
        Thread running method

        - receives raw data from gpsd
        - parses ubx frames, decodes them
        - if a frame is received it is put in the receive queue
        """
        try:
            logger.info('connecting to gpsd')
            self.listen_sock.connect(('127.0.0.1', 2947))
        except socket.error as msg:
            logger.error(msg)
            # TODO: Error handling

        try:
            logger.debug('starting raw listener on gpsd')
            self.listen_sock.send(self.connect_msg)
            self.listen_sock.settimeout(0.25)

            logger.debug('receiver ready')
            self.thread_ready_event.set()

            while not self.thread_stop_event.is_set():
                try:
                    data = self.listen_sock.recv(8192)
                    if data:
                        self.parser.process(data)
                except socket.timeout:
                    pass

        except socket.error as msg:
            logger.error(msg)

        logger.debug('receiver done')
