#!/usr/bin/python3
"""
Changes bitrate of modem

This example uses the TTY server backend to have direct access
to the modem w/o gpsd.

Run as module from project root:
python3 -m examples.change_bitrate <current> <new>

Example:
python3 -m examples.change_bitrate 9600 115200
"""
import argparse
import logging

from ubxlib.server_tty import GnssUBlox
from ubxlib.ubx_cfg_prt import UbxCfgPrtPoll, UbxCfgPrtUart


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
        'tty',
        help="tty of receiver (i.e. /dev/ttyS1)")

    parser.add_argument(
        'current',
        help="current bitrate of receiver", type=int)

    parser.add_argument(
        'new',
        help="new bitrate to set", type=int)

    args = parser.parse_args()
    logger.setLevel(logging.INFO)
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create UBX library
    # Note: tty and baudrate must match current receiver configuration
    ubx = GnssUBlox(args.tty, args.current)
    ubx.setup()

    # Get current tty port settings from modem
    poll_cfg = UbxCfgPrtPoll()
    poll_cfg.f.PortId = UbxCfgPrtPoll.PORTID_Uart

    port_cfg = ubx.poll(poll_cfg)
    if port_cfg:
        print(f'Current port config is\n{port_cfg}')
        print(f'Current modem bitrate is {port_cfg.f.baudRate} bps')

        assert args.current == port_cfg.f.baudRate

        # Set new bitrate
        print(f'Changing bitrate to {args.new}')
        port_cfg.f.baudRate = args.new

        # Note: usually we would use ubx.set() to send the request and wait for an ack
        # Unfortunately the modem changes the bitrate immediately so the ACK is not
        # received.
        ubx.fire_and_forget(port_cfg)

        print('Done, please use detect_bitrate.py to check')
    else:
        print("No answer from modem. Is current bitrate correct?")
        # No answer...
        pass

    ubx.cleanup()


if __name__ == '__main__':
    main()
