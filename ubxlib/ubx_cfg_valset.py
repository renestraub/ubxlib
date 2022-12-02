from .cid import UbxCID
from .frame import UbxFrame
from .types import U1


class UbxCfgValSet_(UbxFrame):
    NAME = 'UBX-CFG-VALSET'
    CID = UbxCID(UbxCID.CLASS_CFG, 0x8a)


class UbxCfgValSetAction(UbxCfgValSet_):
    NAME = UbxCfgValSet_.NAME + '-ACTION'

    # Configuration storage layers
    LAYER_RAM_MASK = 0x01
    LAYER_BBR_MASK = 0x02
    LAYER_FLASH_MASK = 0x04

    def __init__(self, key_values):
        super().__init__()

        if type(key_values) is not list:
            key_values = [key_values]

        assert(len(key_values) >= 1)      # Need at least one key
        assert(len(key_values) <= 64)     # Max. allowed keys per request

        # Register and define fixed fields
        self.f.add(U1('version'))
        self.f.add(U1('layer'))
        self.f.add(U1('res0'))
        self.f.add(U1('res1'))

        self.f.version = 0x00
        self.f.layer = UbxCfgValSetAction.LAYER_RAM_MASK

        # Dynamically add cfg keys, rename provided keys to be in order
        for item, cfgkey in enumerate(key_values):
            name = f'data{item}'
            cfgkey.name = name
            self.f.add(cfgkey)
