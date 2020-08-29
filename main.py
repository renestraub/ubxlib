#!/usr/bin/python3

import binascii
import logging
import time

from ubxlib.cid import UbxCID
from ubxlib.server import GnssUBlox
from ubxlib.ubx_ack import UbxAckAck
from ubxlib.ubx_cfg_cfg import UbxCfgCfgAction
from ubxlib.ubx_cfg_esfalg import UbxCfgEsfAlg, UbxCfgEsfAlgPoll
from ubxlib.ubx_cfg_gnss import UbxCfgGnss, UbxCfgGnssPoll
from ubxlib.ubx_cfg_nav5 import UbxCfgNav5, UbxCfgNav5Poll
from ubxlib.ubx_cfg_nmea import UbxCfgNmea, UbxCfgNmeaPoll
from ubxlib.ubx_cfg_rst import UbxCfgRstAction
from ubxlib.ubx_cfg_tp5 import UbxCfgTp5, UbxCfgTp5Poll
from ubxlib.ubx_esf_alg import UbxEsfAlg, UbxEsfAlgPoll, UbxEsfResetAlgAction
from ubxlib.ubx_esf_status import UbxEsfStatus, UbxEsfStatusPoll
from ubxlib.ubx_mon_ver import UbxMonVer, UbxMonVerPoll
from ubxlib.ubx_nav_status import UbxNavStatus, UbxNavStatusPoll
from ubxlib.ubx_upd_sos import UbxUpdSos, UbxUpdSosAction, UbxUpdSosPoll

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.DEBUG)


"""
msg_cfg_port_poll = bytearray.fromhex('06 00 01 00 01')  # UBX-CFG-PRT poll
msg_nav_status_poll = bytearray.fromhex('01 03 00 00')
"""

# Create UBX library
# ubx = GnssUBlox('/dev/ttyS3')
ubx = GnssUBlox()
ready = ubx.setup()
assert ready

# Register the frame types we use
protocols = [UbxMonVer, UbxEsfStatus, UbxEsfAlg, UbxNavStatus]
for p in protocols:
    ubx.register_frame(p)

#ubx.register_frame(UbxMonVer)
#ubx.register_frame(UbxEsfStatus)
ubx.register_frame(UbxUpdSos)
ubx.register_frame(UbxCfgTp5)
ubx.register_frame(UbxCfgNmea)
ubx.register_frame(UbxCfgGnss)
ubx.register_frame(UbxCfgNav5)
ubx.register_frame(UbxCfgEsfAlg)
#ubx.register_frame(UbxEsfAlg)

"""
# Remove backup
m = UbxUpdSosAction()
m.f.cmd = UbxUpdSosAction.CLEAR
m.pack()
print(m)
print(m.f.cmd)
# quit()

r.expect(UbxAckAck.CID)
r.send(m)
r.wait()
"""

"""
m = UbxCfgRstAction()
m.stop()
m.pack()
ubx.send(m)

time.sleep(2.5)

m = UbxCfgRstAction()
m.start()
m.pack()
ubx.send(m)
"""

m = UbxMonVerPoll()
res = ubx.poll(m)
print(res)

m = UbxCfgNmeaPoll()
res = ubx.poll(m)
print(res)

"""
res.f.nmeaVersion = 0x41
res.pack()
ubx.expect(UbxAckAck.CID)
ubx.set(res)
"""

"""
m = UbxCfgCfgAction()
m.save(UbxCfgCfgAction.MASK_NavConf)    # To save CFG-NAV-NMEA
ubx.set(m)

# Factory reset NAV config
m = UbxCfgCfgAction()
m.reset(UbxCfgCfgAction.MASK_NavConf)    # To save CFG-NAV-NMEA
ubx.set(m)
"""

"""
m = UbxCfgNav5Poll()
res = ubx.poll(m)
print(res)
res.f.dynModel = 4
ubx.set(res)
"""

"""
m = UbxCfgEsfAlgPoll()
res = ubx.poll(m)
print(res)
# res.f.bitfield &= ~UbxCfgEsfAlg.BITFIELD_doAutoMntAlg
res.f.bitfield |= UbxCfgEsfAlg.BITFIELD_doAutoMntAlg
res.f.yaw = 999
res.f.pitch = 888
res.f.roll = 777
ubx.set(res)
"""

"""
m = UbxEsfResetAlgAction()
ubx.set(m)
"""

m = UbxEsfAlgPoll()
res = ubx.poll(m)
print(res)

"""
m = UbxCfgGnssPoll()
res = ubx.poll(m)
print(res)
#res.gps_glonass()
res.gps_galileo_beidou()
print(res)

res.pack()
ubx.expect(UbxAckAck.CID)
ubx.send(res)
ubx.wait()

quit(0)
"""

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
ubx.send(m)

m = UbxMgaIniTimeUtc()
m.set_current_dt()
m.pack()
ubx.send(m)
"""

quit(0)

for i in range(0, 10000):
    print(f'***** {i} ***********************')

    logger.debug('getting SOS state')
    msg_upd_sos_poll = UbxUpdSosPoll()
    res = ubx.poll(msg_upd_sos_poll)
    print(res)
    if res:
        print(f'SOS state is {res.f.response}')

    msg_cfg_tp5_poll = UbxCfgTp5Poll()
    msg_cfg_tp5_poll.f.tpIdx = 1
    # TODO: .pack has to go elsewhere, better hidden in to_bytes()
    msg_cfg_tp5_poll.pack()
    print(msg_cfg_tp5_poll)
    print(binascii.hexlify(msg_cfg_tp5_poll.to_bytes()))
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
    res.pack()

    ubx.expect(UbxAckAck.CID)
    ubx.send(res)
    ubx.wait()

    time.sleep(1.87)

ubx.cleanup()


# TODO: ubx-cfg-nmea
# TODO:  nmea version = 4.10
