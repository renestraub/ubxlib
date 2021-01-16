# ubxlib

u-blox gnss modem library

_A more elaborate description will follow later._


## Quick Start

Code samples can be found in the examples folder. Execute them from
the project directory as modules.

```python
python3 -m examples.show_version
```


### Example - Get Modem Versions

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
