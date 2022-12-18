#!/usr/bin/python3
"""
NEO-M9 sample code to set dynamic model

Run as module from project root:
python3 -m examples.set_dyn_modem_m9
"""
import logging

from ubxlib.server import GnssUBlox     # Working on top of gpsd
# from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.cfgkeys import UbxKeyId, CfgKeyData
from ubxlib.ubx_cfg_valget import UbxCfgValGetPoll
from ubxlib.ubx_cfg_valset import UbxCfgValSetAction


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)

modes = {
    0: "Portable",
    2: "Stationary",
    3: "Pedestrian",
    4: "Automotive",
    5: "Sea",
    6: "Airborne with <1g acceleration",
    7: "Airborne with <2g acceleration",
    8: "Airborne with <4g acceleration",
    9: "Wrist-worn watch (not available in all products)"
}


# Create UBX library
ubx = GnssUBlox('/dev/gnss0')
ubx.setup()

# Show current dynamic model
poll = UbxCfgValGetPoll(UbxKeyId.CFG_NAVSPG_DYNMODEL)
res = ubx.poll(poll)
curr_mode = res.get("data0").value
print()
print(f"Current dynamic model is {modes[curr_mode]} ({curr_mode})")

print()
print("Available modes")
for mode in sorted(modes):
    print(f' {mode}: {modes[mode]}')

mode = int(input('Please select a mode from above list: '))
assert mode in modes

# Create dynamic model config key and apply it
cfgkey_dyn_model = CfgKeyData.from_key(UbxKeyId.CFG_NAVSPG_DYNMODEL, mode)
cfg_setval = UbxCfgValSetAction(cfgkey_dyn_model)

ack_nak = ubx.set(cfg_setval)
print(ack_nak)      # Just print result, no further check

ubx.cleanup()
