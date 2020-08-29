#!/usr/bin/python3
"""
Shows serial port configuration

Run as module from project root:
python3 -m examples.show_port_config
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
ubx = GnssUBlox()
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxCfgPrtUart)

# Poll version from modem
poll_cfg = UbxCfgPrtPoll()
poll_cfg.f.PortId = UbxCfgPrtPoll.PORTID_Uart
res = ubx.poll(poll_cfg)

# Simple print of received answer frame
print(f'Received answer from modem\n{res}')

# Get out protocol as value and string
print(res.get('outProtoMask').value)
print(res.get('outProtoMask').protocols)

ubx.cleanup()
