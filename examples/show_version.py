#!/usr/bin/python3
"""
Simple demonstrator that gets modem version
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_mon_ver import UbxMonVerPoll, UbxMonVer


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
# Note: tty is only used to address modem in gpsd.
#       the library does not use the tty directly
ubx = GnssUBlox('/dev/ttyS3')
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxMonVer)

# Poll version from modem
poll_version = UbxMonVerPoll()
res = ubx.poll(poll_version)

# Simple print of received answer frame
print(f'Received answer from modem\n{res}')

# Can also access fields of UbxMonVer via .f member
print()
print(f'SW Version: {res.f.swVersion}')
print(f'HW Version: {res.f.hwVersion}')

ubx.cleanup()
