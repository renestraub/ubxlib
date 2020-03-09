
class Checksum(object):
    """
    Computes ubx checksum
    """
    def __init__(self):
        super().__init__()

    def value(self):
        return self.cka, self.ckb

    def reset(self):
        self.cka = 0
        self.ckb = 0

    def add(self, byte):
        self.cka += byte
        self.cka &= 0xFF
        self.ckb += self.cka
        self.ckb &= 0xFF
