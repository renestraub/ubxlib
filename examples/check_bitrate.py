#!/usr/bin/python3
"""
Detects current modem bitrate

Theory of operation
- With each supported bitrate the port configuration is queried.
- In case the proper bitrate is selected, the query will succeed
  and the reported bitrate should match.
- If no response is received the next bitrate is tried.
- To save time the number of retries is reduced compared to normal
  operation.
- The maximum timeout is set to 1.5 seconds. Empirical tests have
  shown a maximum response times of:
  -   9600 bps : 1.36 s
  -  19200 bps : 1.42 s
  -  38400 bps : 1.46 s
  -  57600 bps : 1.38 s
  - 115200 bps : 1.40 s

In a real world application the expected bitrate (115200) should
be first in the list, followed by factory default value (9600).

This example uses the TTY server backend to have direct access
to the modem w/o gpsd.

Run as module from project root:
python3 -m examples.check_bitrate
"""
import argparse
import logging

from ubxlib.server_tty import GnssUBlox
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart


TTY = '/dev/gnss0'
BIT_RATES = [9600, 19200, 38400, 57600, 115200]


def detect_bitrate_active(ubx):
    retries = ubx.set_retries(1)
    delay = ubx.set_retry_delay(1500)

    for baud in BIT_RATES:
        logger.info(f'checking {baud} bps')

        ubx.set_baudrate(baud)

        # Try to query current port settings.
        # If bitrate matches we should get a response, reporting the current bitrate
        # Otherwise the request will timeout.
        poll_cfg = UbxCfgPrtPoll()
        poll_cfg.f.PortId = UbxCfgPrtPoll.PORTID_Uart

        res = ubx.poll(poll_cfg)
        if res:
            if res.f.baudRate == baud:
                logger.debug('bitrate matches')
                return baud
            else:
                logger.warning('bitrate reported ({res.f.baudrate} bps) does not match')

        logger.debug(f'bitrate {baud} not working')

    ubx.set_retries(retries)
    ubx.set_retry_delay(delay)


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Detects current UART bitrate of GNSS modem')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='be verbose, show debug output')

    args = parser.parse_args()
    logger.setLevel(logging.INFO)
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ubx = GnssUBlox('/dev/gnss0')
    ubx.setup()
    ubx.register_frame(UbxCfgPrtUart)

    baud = detect_bitrate_active(ubx)
    print(f'baudrate is {baud} bps')

    ubx.cleanup()


if __name__ == '__main__':
    main()
