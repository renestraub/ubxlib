#!/usr/bin/python3
"""
Detects current modem bitrate

There are two possible ways - lets call them active and passive. See details in
the explanation below.

This example uses the TTY server backend to have direct access to the modem w/o
gpsd.

Run as module from project root, e.g.:
python3 -m examples.check_bitrate passive

In a real world application the expected bitrate (e.g. 115200) should be first
in the list, followed by factory default value (9600).

Active Scan
-----------

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

Because of the following behavior the active mode is problematic.

"As of Protocol version 18+, the UART RX interface will be disabled when more
than 100 frame errors are detected during a one-second period.
This can happen if the wrong baud rate is used or the UART RX pin is grounded.
The error message appears when the UART RX interface is re-enabled at the end
of the one-second period."

Empirical tests have shown that sending at 19'200 maximally confuses the receiver.
-> The use of the active scan mode is therefore discouraged.

Passive Scan
------------

- With each supported bitrate a scan is made for UBX or NMEA frames
- If at least two frames are received the current baudrate is considered correct
- If not, the next baudrate is tried

Empirical tests have shown maximum scan intervals of 1.182 s. The default interval
of the scan function is set to 1.5 seconds.
"""
import argparse
import logging
import time

from ubxlib.server_tty import GnssUBlox
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart

TTY = '/dev/gnss0'
# BIT_RATES = [9600, 19200, 38400, 57600, 115200]
# BIT_RATES = [115200, 57600, 38400, 19200, 9600]
BIT_RATES = [115200, 9600]


def detect_bitrate_active(ubx):
    logger.info('active scan')

    ubx.register_frame(UbxCfgPrtUart)

    baud_detected = None
    retries = ubx.set_retries(1)
    delay = ubx.set_retry_delay(1500)

    # Try to query current port settings.
    # If bitrate matches we should get a response, reporting the current bitrate.
    # Otherwise the request will timeout.
    poll_cfg = UbxCfgPrtPoll()
    poll_cfg.f.PortId = UbxCfgPrtPoll.PORTID_Uart

    for baud in BIT_RATES:
        logger.info(f'checking {baud} bps')

        ubx.set_baudrate(baud)

        res = ubx.poll(poll_cfg)
        if res:
            if res.f.baudRate == baud:
                logger.debug('bitrate matches')
                baud_detected = baud
                break
            else:
                logger.warning('bitrate reported ({res.f.baudrate} bps) does not match')
        else:
            logger.debug(f'bitrate {baud} not working')

        # Throttle transmission in order not to trigger receiver frame error detection
        time.sleep(1.0)

    ubx.set_retries(retries)
    ubx.set_retry_delay(delay)

    return baud_detected


def detect_bitrate_passive(ubx):
    logger.info('passive scan')

    for baud in BIT_RATES:
        logger.info(f'checking {baud} bps')

        ubx.set_baudrate(baud)
        if ubx.scan():
            return baud

        logger.debug(f'bitrate {baud} not working')


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

    parser.add_argument(
        'method',
        choices=['passive', 'active'],
        help="selects the scan method")

    args = parser.parse_args()
    logger.setLevel(logging.INFO)
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ubx = GnssUBlox(TTY)
    ubx.setup()

    if 'active' in args.method:
        baud = detect_bitrate_active(ubx)
    else:
        baud = detect_bitrate_passive(ubx)

    print(f'baudrate is {baud} bps')

    ubx.cleanup()


if __name__ == '__main__':
    main()
