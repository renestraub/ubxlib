#!/usr/bin/python3
"""
Sample code to send speed information to modem

NOTE:
- Configuration needs to be done externally
  CFG-NAV5:
  - Dynamic Model: 4: Automotive
  CFG-ESFWT
  - Data Type: Speed
  - Activate WT Signal Pin: Off
  - Scale Factor: 0.0
  - Latency: 10
  - Frequeny: 10
  - Dead-Band: 1.00
  - Speed Error RMS: 0.1

- Requires timepulse connected to GPIO 2_9

Run as module from project root:
python3 -m examples.esf_speed_tp
"""
import logging
import os
import gpiod

from ubxlib.server import GnssUBlox
from ubxlib.ubx_cfg_tp5 import UbxCfgTp5Poll
from ubxlib.ubx_esf_meas import UbxEsfMeas

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


def configure_tp(ubx):
    """
    Configure timepulse to 10 Hz output with 50% duty cycle
    """
    period = int(1000000 * 0.1)  # 10 Hz
    pulse_len = int(period / 2)

    msg_cfg_tp5_poll = UbxCfgTp5Poll()
    msg_cfg_tp5_poll.f.tpIdx = 1
    tp5 = ubx.poll(msg_cfg_tp5_poll)
    if tp5:
        tp5.f.flags = 1 + 2 + 16    # Active, lock to GPS, isLength
        tp5.f.freqPeriod = period
        tp5.f.freqPeriodLock = period
        tp5.f.pulseLenRatio = pulse_len
        tp5.f.pulseLenRatioLock = pulse_len
        ubx.set(tp5)


def io_event_loop(ubx):
    """
    Waits for timepulse event on I/O
    Sends next speed frame
    Do some house keeping for jitter measurement
    """
    data_type_speed = 11      # speed, units = m/s * 1e-3, aka mm/s
    speed = 0   # mm/s
    direction = 1
    time_last = None
    max_jitter = 0.0

    chip = gpiod.Chip('2')
    lines = chip.get_lines([9])     # gpio2_9 = sysboot_3/4
    lines.request(consumer='esf_speed_tp.py', type=gpiod.LINE_REQ_EV_RISING_EDGE)
    logger.info(f'initialized {lines}')

    # ESF Measure Frame to report speed to modem
    # 24.12.2 UBX-ESF-MEAS (0x10 0x02)
    esf_speed = UbxEsfMeas()
    esf_speed.f.flags = 0x0000          # No timemark, no calibration tag
    esf_speed.f.id = 0                  # Identification number of data provider, shall be 0

    count = 0
    while True:
        ev_lines = lines.event_wait(sec=10)
        if ev_lines:
            for line in ev_lines:
                event = line.event_read()
                time_event = event.sec + event.nsec / 1e9
                time_event_ms = int(time_event * 1000) & 0xFFFFFFFF

                # Prepare next frame
                esf_speed.f.timeTag = time_event_ms
                esf_speed.f.data = (speed & 0xFFFFFF) | data_type_speed << 24
                # logger.info(f'sending frame {i}')
                ubx.fire_and_forget(esf_speed)

                # Update simulated speed information
                speed += direction
                if speed == 500:
                    direction = -1
                if speed == 0:
                    direction = 1

                # Jitter measurement and occasional display
                if time_last:
                    jitter_sec = time_event - (time_last + 0.1)
                    if abs(jitter_sec) > max_jitter:
                        max_jitter = abs(jitter_sec)

                    if count % 20 == 0:
                        logger.info(f'jitter {jitter_sec*1e3:.3f} msecs, max. {max_jitter*1e3:.3f} msecs')

                time_last = time_event
                count += 1


def main():
    os.nice(-10)

    ubx = GnssUBlox()
    ubx.setup()

    configure_tp(ubx)
    io_event_loop(ubx)

    ubx.cleanup()


if __name__ == "__main__":
    main()
