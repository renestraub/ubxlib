#!/usr/bin/python3
"""
Shows serial port configuration

Run as module from project root:
python3 -m examples.show_port_config
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.server_tty import GnssUBlox as GnssUBloxTTY    # TTY direct backend
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
# ubx = GnssUBlox()
ubx = GnssUBloxTTY('/dev/gnss0', 115200)
res = ubx.setup()
if not res:
    print('Cannot setup library')
    quit(10)


# Register the frame types we use
ubx.register_frame(UbxCfgPrtUart)

# Poll version from modem
poll_cfg = UbxCfgPrtPoll()
poll_cfg.f.PortId = UbxCfgPrtPoll.PORTID_Uart
res = ubx.poll(poll_cfg)
if res:
    # Simple print of received answer frame
    print(f'Received answer from modem\n{res}')

    # Get out protocol as value and string
    print(res.get('outProtoMask').value)
    print(res.get('outProtoMask').protocols)
else:
    print('Poll failed')

ubx.cleanup()
