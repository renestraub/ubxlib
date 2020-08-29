#!/usr/bin/python3
"""
Sample code to change used GNSS systems

Run as module from project root:
python3 -m examples.set_gnss_systems
"""
import logging

from ubxlib.server import GnssUBlox
# from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.ubx_cfg_gnss import UbxCfgGnssPoll, UbxCfgGnss


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
ubx = GnssUBlox()
# ubx = GnssUBlox('/dev/gnss0', 115200)
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxCfgGnss)

# Query modem for current protocol settings
poll_nmea_cfg = UbxCfgGnssPoll()
res = ubx.poll(poll_nmea_cfg)
print(res)

# Change the GNSS systems
res.gps_galileo_beidou()

# By adding the following line an incorrect system constellation is selected
# The receiver will reject this request with a NAK
# res.enable_gnss(UbxCfgGnss.GNSS_GLONASS)

# Send command to modem, result is ack_nak from modem
ack_nak = ubx.set(res)
if ack_nak:
    print(ack_nak)      # Just print result, could also check for ACK-ACK CID
else:
    print('Some sort of error happened')

ubx.cleanup()
