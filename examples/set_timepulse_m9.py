#!/usr/bin/python3
"""
NEO-M9 sample code to configure timepulse
- Unlocked: 1 kHZ, 50% duty cycle
- Locked: 1 kHZ, 25% duty cycle

Run as module from project root:
python3 -m examples.set_timepulse_m9
"""
import logging

# from ubxlib.server import GnssUBlox
from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.cfgkeys import UbxKeyId, CfgKeyData
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


cfgkey_tp2_ena = CfgKeyData.from_key(UbxKeyId.CFG_TP_TP2_ENA, True)             # TP enabled
cfgkey_tp_pulse_def = CfgKeyData.from_key(UbxKeyId.CFG_TP_PULSE_DEF, 0)         # Specify pulse interval in us
cfgkey_tp_len_def = CfgKeyData.from_key(UbxKeyId.CFG_TP_PULSE_LENGTH_DEF, 1)    # Specify pulse lengths in us
cfgkey_pol_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_POL_TP2, 1)                # Rising edge at top of second
cfgkey_grid_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_TIMEGRID_TP2, 1)          # Lock to GPS time
cfgkey_align_to = CfgKeyData.from_key(UbxKeyId.CFG_TP_ALIGN_TO_TOW_TP2, True)   # Align pulse to top of seconds

cfgkey_period_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_PERIOD_TP2, 1000)       # 1000 us = 1 kHz
cfgkey_len_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_LEN_TP2, 500)              # 50% duty cycle

cfgkey_use_locked_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_USE_LOCKED_TP2, True)       # Use following settings when locked
cfgkey_period_lock_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_PERIOD_LOCK_TP2, 1000)     # 1000 us = 1 kHz
cfgkey_len_lock_tp2 = CfgKeyData.from_key(UbxKeyId.CFG_TP_LEN_LOCK_TP2, 250)            # 25% duty cycle

# Create CFG-VALSET message with the 4 configuration keys
cfg_setval = UbxCfgValSetAction([
    cfgkey_tp2_ena, cfgkey_tp_pulse_def, cfgkey_tp_len_def, 
    cfgkey_pol_tp2, cfgkey_grid_tp2, cfgkey_align_to,
    cfgkey_period_tp2, cfgkey_len_tp2,
    cfgkey_use_locked_tp2, cfgkey_period_lock_tp2, cfgkey_len_lock_tp2
])

# Post message and check ACK/NAK result
ack_nak = ubx.set(cfg_setval)
print(ack_nak)      # Just print result, no further check

ubx.cleanup()
