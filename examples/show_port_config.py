#!/usr/bin/python3
"""
Shows serial port configuration
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('gnss_tool')
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


# Create UBX library
# Note: tty is only used to address modem in gpsd.
#       the library does not use the tty directly
ubx = GnssUBlox('/dev/ttyS3')
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
