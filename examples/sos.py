#!/usr/bin/python3
"""
Application to handle Save-On-Shutdown

This example uses the tty backend that accesses the modem directly (w/o gpsd).
Ensure gpsd is stopped when running.

Run as module from project root with start or stop argument:
python3 -m examples.sos [start|stop]

Theorie of operation

Start:
- Enable acknowledge messages for aiding requests
- Set UTC time to receiver. This is mandatory when recovering from an SoS
  state. If time is not set the next SoS backup will be invalid.
- Check if a backup was present and if so remove it 

Stop
- Stop the GNSS receiver function, so that the modem state is stable
- Create SoS backup
"""
import argparse
import datetime
import logging
import time

# from ubxlib.cid import UbxCID
from ubxlib.server_tty import GnssUBlox
from ubxlib.ubx_cfg_navx5 import UbxCfgNavx5, UbxCfgNavx5Poll
from ubxlib.ubx_cfg_rst import UbxCfgRstAction
from ubxlib.ubx_mga_ini_time_utc import UbxMgaIniTimeUtc
from ubxlib.ubx_mon_ver import UbxMonVer, UbxMonVerPoll
from ubxlib.ubx_upd_sos import UbxUpdSos, UbxUpdSosAction, UbxUpdSosPoll


def show_version(ubx):
    # Poll version from modem
    poll_version = UbxMonVerPoll()
    res = ubx.poll(poll_version)
    if res:
        # Simple print of received answer frame
        logger.debug(f'Received answer from modem\n{res}')

        # Can also access fields of UbxMonVer via .f member
        logger.info(f'SW Version: {res.f.swVersion}')
        logger.info(f'HW Version: {res.f.hwVersion}')
    else:
        logger.warning('no answer from modem')


def check_sos_state(ubx):
    logger.info("checking SoS state")

    state = None
    poll_sos = UbxUpdSosPoll()
    res = ubx.poll(poll_sos)

    if res:
        responses = ["Unknown", "Failed restoring", "Restored", "Not restored (no backup)"]
        if 0 <= res.f.response <= 3:
            state = res.f.response
            logger.info(f'state: {responses[res.f.response]}')
        else:
            logger.warning(f'state: <unknown>')

    return state


def create_backup(ubx):
    logger.info("creating backup")

    sos = UbxUpdSosAction()
    sos.backup()
    res = ubx.poll(sos)
    if res:
        if res.f.cmd == 2 and res.f.response == 1:
            logger.info('backup created')
            return True

    logger.warning('error creating backup')


def remove_backup(ubx):
    logger.info('removing backup')

    sos = UbxUpdSosAction()
    sos.clear()

    # This request is neither ACK'ed, nor a response is available
    ubx.send(sos)
    logger.info('backup removed (no error check possible)')


def stop_receiver(ubx):
    logger.info('stopping receiver')

    rst_msg = UbxCfgRstAction()
    rst_msg.stop()
    ubx.send(rst_msg)
    # TODO: check if an ACK is sent for stop() command
    time.sleep(1.0)


def enable_mga_ack(ubx):
    logger.info('enabling ACK for assistance messages')

    navx5poll = UbxCfgNavx5Poll()
    navx5 = ubx.poll(navx5poll)
    if navx5:
        # logger.debug(navx5)
        navx5.f.mask1 = UbxCfgNavx5.MASK1_AckAid
        navx5.f.mask2 = 0
        navx5.f.ackAiding = 1
        res = ubx.set(navx5)
        if res:
            logger.info("ACKs enabled")
            return True

    logger.warning('enabling ACK failed')


def set_time(ubx):
    logger.info('setting receiver time')

    init_time = UbxMgaIniTimeUtc()
    dt = datetime.datetime.utcnow()
    init_time.set_datetime(dt)

    # res = ubx.send(init_time)       # When MGA flow control is disabled
    # res = True
    res = ubx.set_mga(init_time)    # When flow control is enabled
    if res:
        logger.info(f'time set to {dt}')
        return True

    logger.warning('setting time failed')


FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Manages GNSS modem')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='be verbose, show debug output')

    parser.add_argument(
        'action',
        choices=['start', 'stop'],
        help="selects action to perform")

    args = parser.parse_args()
    logger.setLevel(logging.INFO)
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create UBX library
    ubx = GnssUBlox('/dev/gnss0')
    ubx.setup()

    # Register the frame types we use
    ubx.register_frame(UbxMonVer)
    ubx.register_frame(UbxUpdSos)
    ubx.register_frame(UbxCfgNavx5)

    # Execute desired commands
    # show_version(ubx)

    if args.action == 'start':
        # Set UTC time so that recovery from 2D-DR also works
        enable_mga_ack(ubx)

        set_time(ubx)
        time.sleep(0.5)
        set_time(ubx)

        # Check if a backup was present
        res = check_sos_state(ubx)
        if res == 2:
            remove_backup(ubx)

    elif args.action == 'stop':
        stop_receiver(ubx)
        create_backup(ubx)
    else:
        logger.warning(f'unknown command {args.action}')

    ubx.cleanup()


if __name__ == '__main__':
    main()
