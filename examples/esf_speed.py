#!/usr/bin/python3
"""
Sample code to send speed information to modem

NOTE:
- Completely untested
- Configuration (GAWT mode) needs to be done externally

Run as module from project root:
python3 -m examples.esf_speed
"""
import logging
import time

from ubxlib.server import GnssUBlox
from ubxlib.ubx_esf_meas import UbxEsfMeas


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
# ubx.register_frame(UbxEsfSpeed)

# ESF Measure Frame to report speed to modem
# 24.12.2 UBX-ESF-MEAS (0x10 0x02)

esf_speed = UbxEsfMeas()
esf_speed.f.timeTag = 0             # should most likely be set to some reasonable value
esf_speed.f.flags = 0x00000000      # No timemark, no calibration tag
esf_speed.f.id = 0x0002             # Identification number of data provider, no idea what this is


for i in range(1000):
    logger.info(f'sending frame {i}')

    speed = 0
    data_type = 11      # speed, units = m/s * 1e-3, aka mm/s
    esf_speed.f.data = (speed & 0xFFFFFF) | data_type << 24
    esf_speed.pack()
    ubx.send(esf_speed)

    # Poor mans 10 Hz timer -> replace with gpio event (gpiod)
    time.sleep(0.1)

ubx.cleanup()
