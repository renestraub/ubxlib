
class Checksum(object):
    """
    Computes ubx checksum
    """
    def __init__(self):
        super().__init__()
        self.reset()

    def value(self):
        return self._cka, self._ckb

    def matches(self, cka, ckb):
        return self._cka == cka and self._ckb == ckb

    def reset(self):
        self._cka = 0
        self._ckb = 0

    def add(self, byte):
        self._cka += byte
        self._cka &= 0xFF
        self._ckb += self._cka
        self._ckb &= 0xFF
