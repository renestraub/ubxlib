#!/usr/bin/python3
"""
Gets current modem bitrate and changes it

When bitrate is 115'200 it is changed to 9'600 and vice versa.

This example uses the TTY server backend to have direct access
to the modem w/o gpsd.

Run as module from project root:
python3 -m examples.change_bitrate
"""
import logging

from ubxlib.server_tty import GnssUBloxBitrate
from ubxlib.server_tty import GnssUBlox
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart


TTY = '/dev/ttyS3'

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
# logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.WARNING)


# Check current bitrate of modem
ubx_bitrate = GnssUBloxBitrate(TTY)

print('Determining current bitrate')
bitrate = ubx_bitrate.determine()

print(f'Current GNSS receiver bitrate is {bitrate} bps')
assert bitrate


# Create UBX library
# Note: tty and baudrate must match current receiver configuration
ubx = GnssUBlox(TTY, bitrate)
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxCfgPrtUart)

# Poll current tty port settings from modem
poll_cfg = UbxCfgPrtPoll()
poll_cfg.f.PortId = UbxCfgPrtPoll.PORTID_Uart

port_cfg = ubx.poll(poll_cfg)
if port_cfg:
    print(f'Current port config is\n{port_cfg}')
    print(f'Current modem bitrate is {port_cfg.f.baudRate} bps')
    if port_cfg.f.baudRate == 115200:
        print('Changing bitrate to 9600')
        port_cfg.f.baudRate = 9600
    else:
        print('Changing bitrate to 115200')
        port_cfg.f.baudRate = 115200

    # Note: usually we would use ubx.set() to send the request and wait for an ack
    # Unfortunately the modem changes the bitrate immediately so the ACK is not
    # received.
    port_cfg.pack()
    ubx.send(port_cfg)

    print('done, please re-run to check effect')
else:
    # No answer...
    pass

ubx.cleanup()
