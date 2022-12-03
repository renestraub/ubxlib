# ubxlib

u-blox gnss modem library

_A more elaborate description will follow later._


## Quick Start

Code samples can be found in the examples folder. Execute them from
the project directory as modules.

```python
python3 -m examples.show_version
```

## Examples

### Get Modem Versions (NEO-M8, NEO-M9)

The following code is from `examples/show_version.py`.

```python
#!/usr/bin/python3
"""
Simple demonstrator that gets modem version

Accesses first GNSS modem registered with gpsd daemon.

Run as module from project root:
python3 -m examples.show_version
"""
import logging

from ubxlib.server import GnssUBlox
from ubxlib.ubx_mon_ver import UbxMonVerPoll

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)

# Create UBX library
ubx = GnssUBlox()
ubx.setup()

# Poll version from modem
poll_version = UbxMonVerPoll()
res = ubx.poll(poll_version)
if res:
    # Simple print of received answer frame
    print(f'Received answer from modem\n{res}')

    # Can also access fields of UbxMonVer via .f member
    print()
    print(f'SW Version: {res.f.swVersion}')
    print(f'HW Version: {res.f.hwVersion}')
else:
    print('no answer from modem')

ubx.cleanup()
```


### Configure Timepulse (NEO-M9 UBX-CFG-VALSET Mode)

The following code is from `examples/set_timepulse_m9.py`.

```python
#!/usr/bin/python3
"""
NEO-M9 sample code to configure timepulse
- Unlocked: 1 kHz, 50% duty cycle
- Locked: 1 kHz, 25% duty cycle

Run as module from project root:
python3 -m examples.set_timepulse_m9
"""
import logging

from ubxlib.server_tty import GnssUBlox     # TTY direct backend
from ubxlib.cfgkeys import UbxKeyId, CfgKeyValues
from ubxlib.ubx_cfg_valset import UbxCfgValSetAction

FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ubxlib')
logger.setLevel(logging.INFO)

# Create UBX library, assumes 115'200 bps when using TTY backend
ubx = GnssUBlox('/dev/gnss0')
ubx.setup()

# Define configuration,
#  Set key = value pairs
#  Convert them to a list of CfgKeyData items for UbxCfgValSetAction()
cfg_keyvals = CfgKeyValues.from_keyvalues([
    (UbxKeyId.CFG_TP_TP2_ENA, True),            # TP enabled
    (UbxKeyId.CFG_TP_PULSE_DEF, 0),             # Specify pulse interval in us
    (UbxKeyId.CFG_TP_PULSE_LENGTH_DEF, 1),      # Specify pulse lengths in us
    (UbxKeyId.CFG_TP_POL_TP2, 1),               # Rising edge at top of second
    (UbxKeyId.CFG_TP_TIMEGRID_TP2, 1),          # Lock to GPS time
    (UbxKeyId.CFG_TP_ALIGN_TO_TOW_TP2, True),   # Align pulse to top of seconds

    (UbxKeyId.CFG_TP_PERIOD_TP2, 1000),         # 1000 us = 1 kHz
    (UbxKeyId.CFG_TP_LEN_TP2, 500),             # 50% duty cycle

    (UbxKeyId.CFG_TP_USE_LOCKED_TP2, True),     # Use following settings when locked
    (UbxKeyId.CFG_TP_PERIOD_LOCK_TP2, 1000),    # 1000 us = 1 kHz
    (UbxKeyId.CFG_TP_LEN_LOCK_TP2, 250),        # 25% duty cycle]
])

# Create CFG-VALSET message with the configuration key/values
cfg_setval = UbxCfgValSetAction(cfg_keyvals)

# Post message and check ACK/NAK result
ack_nak = ubx.set(cfg_setval)
print(ack_nak)      # Just print result, no further check

ubx.cleanup()
```
