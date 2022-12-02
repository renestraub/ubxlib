# import logging

from .cid import UbxCID
from .frame import UbxFrame
from .types import U1, U2, U4, Fields
from .cfgkeys import CfgKeyData


# TODO: Remove
# logger = logging.getLogger(__name__)


class UbxCfgValGet_(UbxFrame):
    NAME = 'UBX-CFG-VALGET'
    CID = UbxCID(UbxCID.CLASS_CFG, 0x8b)


class UbxCfgValGetPoll(UbxCfgValGet_):
    NAME = UbxCfgValGet_.NAME + '-POLL'

    # Configuration storage layers
    LAYER_RAM = 0
    LAYER_BBR = 1
    LAYER_FLASH = 2
    LAYER_DEFAULT = 7

    def __init__(self, keys):
        super().__init__()

        if type(keys) is not list:
            keys = [keys]

        assert(len(keys) >= 1)      # Need at least one key
        assert(len(keys) <= 64)     # Max. allowed keys per request

        # Register and define fixed fields
        self.f.add(U1('version'))
        self.f.add(U1('layer'))
        self.f.add(U2('position'))

        self.f.version = 0x00
        self.f.layer = UbxCfgValGetPoll.LAYER_RAM
        self.f.position = 0     # Don't skip any key values

        # Dynamically add cfg keys
        for item, cfgkey in enumerate(keys):
            key = U4(f'key{item}')
            key.value = cfgkey
            self.f.add(key)

    def _cls_response(self):
        return UbxCfgValGet


class UbxCfgValGet(UbxCfgValGet_):
    def __init__(self):
        super().__init__()

    def unpack(self):
        # TODO: Error check, minimal frame length

        # Add fixed fields and unpack their values
        self.f = Fields()
        self.f.add(U1('version'))
        self.f.add(U1('layer'))
        self.f.add(U2('position'))
        work_data = super().unpack()

        # Parse variable content of response
        item = 0
        while len(work_data) >= 4:
            # logger.info(f'{len(work_data)}, {work_data}')

            # Extract one cfg key/data pair and add to object
            cfgkey = CfgKeyData(f'data{item}')
            consumed_bytes = cfgkey.unpack(work_data)
            # logger.info(cfgkey)
            self.f.add(cfgkey)

            # Advance to next entry
            item += 1
            work_data = work_data[consumed_bytes:]
            # logger.info(f'consumed bytes {consumed_bytes}')

        # TODO: Error check, no extra data
