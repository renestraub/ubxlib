#!/usr/bin/python3

import logging
import time

# from ubxlib.server import GnssUBlox
from ubxlib.server_tty import GnssUBlox     # TTY direct backend
# from ubxlib.ubx_cfg_cfg import UbxCfgCfgAction
# from ubxlib.ubx_cfg_esfalg import UbxCfgEsfAlg
from ubxlib.ubx_cfg_nav5 import UbxCfgNav5Poll
from ubxlib.ubx_cfg_nmea import UbxCfgNmeaPoll
# from ubxlib.ubx_cfg_rst import UbxCfgRstAction
from ubxlib.ubx_cfg_tp5 import UbxCfgTp5Poll
from ubxlib.ubx_esf_alg import UbxEsfAlgPoll
from ubxlib.ubx_esf_status import UbxEsfStatusPoll
from ubxlib.ubx_mon_ver import UbxMonVerPoll
from ubxlib.ubx_nav_status import UbxNavStatusPoll

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.DEBUG)

# Create UBX library
ubx = GnssUBlox('/dev/gnss0')
# ubx = GnssUBlox()

ready = ubx.setup()
assert ready


m = UbxMonVerPoll()
res = ubx.poll(m)
print(res)

m = UbxCfgNmeaPoll()
res = ubx.poll(m)
print(res)

"""
m = UbxCfgCfgAction()
m.save(UbxCfgCfgAction.MASK_NavConf)    # To save CFG-NAV-NMEA
ubx.set(m)

# Factory reset NAV config
m = UbxCfgCfgAction()
m.reset(UbxCfgCfgAction.MASK_NavConf)    # To save CFG-NAV-NMEA
ubx.set(m)
"""

m = UbxCfgNav5Poll()
res = ubx.poll(m)
print(res)
"""
res.f.dynModel = 4
ubx.set(res)
"""

m = UbxEsfAlgPoll()
res = ubx.poll(m)
print(res)

m = UbxEsfStatusPoll()
res = ubx.poll(m)
print(res)

m = UbxNavStatusPoll()
res = ubx.poll(m)
print(res)

"""
m = UbxCfgRstAction()
m.cold_start()
m.pack()
ubx.fire_and_forget(m)
"""

quit(0)

for i in range(0, 100):
    print(f'***** {i} ***********************')

    msg_cfg_tp5_poll = UbxCfgTp5Poll()
    msg_cfg_tp5_poll.f.tpIdx = 1
    print(msg_cfg_tp5_poll)
    # print(binascii.hexlify(msg_cfg_tp5_poll.to_bytes()))
    res = ubx.poll(msg_cfg_tp5_poll)
    print(res)
    if i > 1:
        assert res.f.pulseLenRatio == 500

    res.f.flags &= ~0x01
    # res.fields['flags'] = 1 + 2 + 16    # Active, lock to GPS, isLength
    res.f.freqPeriod = 1000     # 1 us = kHz
    res.f.freqPeriodLock = 1000     # 1 us = kHz
    res.f.pulseLenRatio = 500   # 500 ns = 50% duty cycle
    res.f.pulseLenRatioLock = 250   # 250 ns = 25% duty cycle
    # print(res)

    ack = ubx.set(res)
    print(ack)

    time.sleep(1.87)

ubx.cleanup()
