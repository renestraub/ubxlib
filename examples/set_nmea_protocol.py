#!/usr/bin/python3
"""
Sample code to change NMEA protocol version used

Run as module from project root:
python3 -m examples.set_nmea_protocol
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_cfg_nmea import UbxCfgNmeaPoll, UbxCfgNmea


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
ubx = GnssUBlox()
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxCfgNmea)

# Query modem for current protocol settings
poll_nmea_cfg = UbxCfgNmeaPoll()
res = ubx.poll(poll_nmea_cfg)

proto_ver = res.f.nmeaVersion // 16     # Protovol is encoded in high/low nibble
proto_rev = res.f.nmeaVersion % 16      # e.g. 0x40 = 4.0
print(f'current NMEA protocol version is {proto_ver}.{proto_rev}')

# Now change to something different
# res.f.nmeaVersion = 0x40
res.f.nmeaVersion = 0x41

# Send command to modem, result is ack_nak from modem
ack_nak = ubx.set(res)
print(ack_nak)      # Just print result, could also check for ACK-ACK CID

ubx.cleanup()
