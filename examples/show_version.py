#!/usr/bin/python3
"""
Simple demonstrator that gets modem version

Run as module from project root:
python3 -m examples.show_version
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_mon_ver import UbxMonVerPoll, UbxMonVer


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
ubx = GnssUBlox()
ubx.setup()

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
