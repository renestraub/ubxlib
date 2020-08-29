#!/usr/bin/python3
"""
Shows status of extended sensor fusion

Run as module from project root:
python3 -m examples.show_esf_status
"""
import logging
import time

from ubxlib.server import GnssUBlox
from ubxlib.ubx_esf_status import UbxEsfStatusPoll, UbxEsfStatus


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


# Create UBX library
ubx = GnssUBlox()
ubx.setup()

# Register the frame types we use
ubx.register_frame(UbxEsfStatus)

# Get state and print in full once
res = ubx.poll(UbxEsfStatusPoll())
print(f'Received answer from modem\n{res}')

print('Checking state, press CTRL+C to abort')

try:
    esf_status_request = UbxEsfStatusPoll()
    while True:
        res = ubx.poll(esf_status_request)
        print(f'GNSS time of week {res.f.iTow}')
        print(f'  {res.get("fusionMode")} (value: {res.get("fusionMode").value})')
        print(f'  {res.get("initStatus1")}')
        print(f'  {res.get("initStatus2")}')

        time.sleep(1.0)

except KeyboardInterrupt:
    print()
    print('Done')

ubx.cleanup()
