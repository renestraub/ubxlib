#!/usr/bin/python3
"""
Sample code to set level arm for
- IMU to VRP (vehicle reference point)
- Antenna to VRP

Run as module from project root:
python3 -m examples.set_lever_arm
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_cfg_esfla import UbxCfgEsflaPoll, UbxCfgEsfla, UbxCfgEsflaSet


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# Create UBX library
ubx = GnssUBlox()
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxCfgEsfla)

# Query modem for current lever arm settings
poll_esfla = UbxCfgEsflaPoll()
res = ubx.poll(poll_esfla)
print(res)    # Shows complete result, usually 5 lever arm settings

# Check indivual settings
lever_IMU = res.lever_arm(UbxCfgEsflaSet.TYPE_VRP_IMU)
lever_antenna = res.lever_arm(UbxCfgEsflaSet.TYPE_VRP_Antenna)
print(f'VRP-to-IMU     : {lever_IMU}')
print(f'VRP-to-Antenna : {lever_antenna}')
res = None

# Construct message with settings for IMU to VRP distance
set_esfla_imu = UbxCfgEsflaSet()
set_esfla_imu.set(UbxCfgEsflaSet.TYPE_VRP_IMU, -10, 38, 30)
ack_nak = ubx.set(set_esfla_imu)
print(ack_nak)      # Just print result, could also check for ACK-ACK CID
set_esfla_imu = None

# Construct message with settings for IMU to Antenna distance
set_esfla_antenna = UbxCfgEsflaSet()
set_esfla_antenna.set(UbxCfgEsflaSet.TYPE_VRP_Antenna, 25, 0, 95)
ack_nak = ubx.set(set_esfla_antenna)
print(ack_nak)
set_esfla_antenna = None

ubx.cleanup()
