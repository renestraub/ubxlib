#!/usr/bin/python3
"""
NEO-M9 sample code to change navigation output rate

Run as module from project root:
python3 -m examples.set_nav_rate_m9
"""
import logging

# from ubxlib.server import GnssUBlox   # gpsd socket
from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.cfgkeys import UbxKeyId, CfgKeyData
from ubxlib.ubx_cfg_valset import UbxCfgValSetAction


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


rate = int(input('Please enter desired rate in Hz (1..5): '))
assert 1 <= rate <= 5
period_in_ms = int(1000/rate)

# Create UBX library
# ubx = GnssUBlox()
ubx = GnssUBlox('/dev/gnss0')
ubx.setup()

# Create measurement rate config key
# Value = Nominal time between GNSS measurements in [ms], e.g. 100 ms results in
# 10 Hz measurement rate.
cfgkey_rate_measure = CfgKeyData.from_key(UbxKeyId.CFG_RATE_MEAS, period_in_ms)

# Set desired rate. Note: Compared to M8 receivers no readback - modify of whole
# RATE settings is needed, just set configuration value CFG_RATE_MEAS.
cfg_setval = UbxCfgValSetAction([cfgkey_rate_measure])

ack_nak = ubx.set(cfg_setval)
print(ack_nak)      # Just print result, no further check


ubx.cleanup()
