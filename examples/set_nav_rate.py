#!/usr/bin/python3
"""
Sample code to change navigation output rate to 2 Hz

Run as module from project root:
python3 -m examples.set_nav_rate
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_cfg_rate import UbxCfgRatePoll, UbxCfgRate


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)


rate = int(input('Please enter desired rate in Hz (1..5): '))
assert 1 <= rate <= 5

# Create UBX library
ubx = GnssUBlox()
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxCfgRate)

# Query modem for current rate settings
poll_rate_cfg = UbxCfgRatePoll()
res = ubx.poll(poll_rate_cfg)
print(res)

# Now change to desired navigation output rate
res.set_rate_in_hz(rate)

# Send command to modem, result is ack_nak from modem
ack_nak = ubx.set(res)
print(ack_nak)      # Just print result, could also check for ACK-ACK CID

ubx.cleanup()
