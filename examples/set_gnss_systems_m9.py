#!/usr/bin/python3
"""
NEO-M9 sample code to change used GNSS systems

Run as module from project root:
python3 -m examples.set_gnss_systems_m9

The demo works by changing the major constellation enable configuration.
I.e. config key CFG-SIGNAL-GAL_ENA.
"""
import logging

# from ubxlib.server import GnssUBlox
from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.types import CfgKeyData
from ubxlib.cfgkeys import UbxKeyId
from ubxlib.ubx_cfg_valget import UbxCfgValGetPoll
from ubxlib.ubx_cfg_valset import UbxCfgValSetAction


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


# Create UBX library
# ubx = GnssUBlox()
ubx = GnssUBlox('/dev/gnss0', 115200)
ubx.setup()


# Read currently active GNSS systems

poll_signals = UbxCfgValGetPoll([
    UbxKeyId.CFG_SIGNAL_GPS_ENA,        # Result will be in data0
    UbxKeyId.CFG_SIGNAL_GPS_L1CA_ENA,
    UbxKeyId.CFG_SIGNAL_GAL_ENA,
    UbxKeyId.CFG_SIGNAL_GAL_E1_ENA,
    UbxKeyId.CFG_SIGNAL_BDS_ENA,
    UbxKeyId.CFG_SIGNAL_BDS_B1_ENA,
    UbxKeyId.CFG_SIGNAL_GLO_ENA,
    UbxKeyId.CFG_SIGNAL_GLO_L1_ENA,
    UbxKeyId.CFG_SIGNAL_SBAS_ENA,
    UbxKeyId.CFG_SIGNAL_SBAS_L1CA_ENA        # Result will be in data9
])

res = ubx.poll(poll_signals)
print(f'Current GNSS system configuration\n{res}')


# Disable BDS and Glonass systems in two different ways
# Note: data type is "one bit", valid values are 0 and 1

#  Method 1) Modify received config keys 
cfgkey_sig_bds = res.get('data4')
cfgkey_sig_bds_b1 = res.get('data5')
cfgkey_sig_bds.value = False
cfgkey_sig_bds_b1.value = False

#  Method 2) Construct keys from scratch
cfgkey_sig_glo = CfgKeyData.from_key(UbxKeyId.CFG_SIGNAL_GLO_ENA, False)
cfgkey_sig_glo_l1 = CfgKeyData.from_key(UbxKeyId.CFG_SIGNAL_GLO_L1_ENA, False)

# Create CFG-VALSET message with the 4 configuration keys
cfg_setval = UbxCfgValSetAction([
    cfgkey_sig_bds, cfgkey_sig_bds_b1, cfgkey_sig_glo, cfgkey_sig_glo_l1
])

# Post message and check ACK/NAK result
ack_nak = ubx.set(cfg_setval)
print(ack_nak)      # Just print result, no further check

ubx.cleanup()
