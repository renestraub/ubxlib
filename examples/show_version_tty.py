#!/usr/bin/python3
"""
Simple demonstrator that gets modem version

In contrast to show_version.py this example uses the
tty backend that accesses the modem directly (w/o gpsd).
Ensure gpsd is stopped when running.

Run as module from project root:
python3 -m examples.show_version_tty
"""
import logging

from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.ubx_mon_ver import UbxMonVerPoll, UbxMonVer


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
# Note: tty and baudrate must match current receiver configuration
ubx = GnssUBlox('/dev/gnss0', 115200)
res = ubx.setup()
if not res:
    print('Cannot setup library')
    quit(10)

# Register the frame types we use
ubx.register_frame(UbxMonVer)

# Poll version from modem
poll_version = UbxMonVerPoll()
res = ubx.poll(poll_version)
if res:
    # Simple print of received answer frame
    print(f'Received answer from modem\n{res}')

    # Can also access fields of UbxMonVer via .f member
    print()
    print(f'SW Version: {res.f.swVersion}')
    print(f'HW Version: {res.f.hwVersion}')
else:
    print('no answer from modem')

ubx.cleanup()
