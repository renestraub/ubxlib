import logging
import struct

from ubxlib.checksum import Checksum


logger = logging.getLogger('gnss_tool')


class U1(object):
    def __init__(self, name):
        self.name = name
        self.pack = 'B'


class I2(object):
    def __init__(self, name):
        self.name = name
        self.pack = 'h'


class I4(object):
    def __init__(self, name):
        self.name = name
        self.pack = 'I'


class X4(object):
    def __init__(self, name):
        self.name = name
        self.pack = 'I'


class UbxCID(object):
    def __init__(self, cls, id):
        super().__init__()
        self.cls = cls
        self.id = id

    def __eq__(self, value):
        return self.cls == value.cls and self.id == value.id

    def __str__(self):
        return f'cls:{self.cls:02x} id:{self.id:02x}'


class UbxFrame(object):
    CID = UbxCID(0, 0)
    NAME = 'UBX'

    SYNC_1 = 0xb5
    SYNC_2 = 0x62

    @classmethod
    def construct(cls, data):
        obj = cls()
        obj.data = data
        obj.unpack()
        return obj

    @classmethod
    def MATCHES(cls, cid):
        return cls.CID == cid

    def __init__(self):
        super().__init__()
        self.data = bytearray()
        self.checksum = Checksum()
        self.fields = dict()
        self.field_list = []

    def to_bytes(self):
        self._calc_checksum()

        msg = bytearray([UbxFrame.SYNC_1, UbxFrame.SYNC_2])
        msg.append(self.CID.cls)
        msg.append(self.CID.id)

        length = len(self.data)
        msg.append((length >> 0) % 0xFF)
        msg.append((length >> 8) % 0xFF)

        msg += self.data
        msg.append(self.cka)
        msg.append(self.ckb)

        return msg

    def _calc_checksum(self):
        self.checksum.reset()

        self.checksum.add(self.CID.cls)
        self.checksum.add(self.CID.id)

        length = len(self.data)
        self.checksum.add((length >> 0) & 0xFF)
        self.checksum.add((length >> 8) & 0xFF)

        for d in self.data:
            self.checksum.add(d)

        self.cka, self.ckb = self.checksum.value()

    # Field functions
    # TODO: Subclass Fields

    def add_field(self, field):
        # Create named entry in dictionary for value
        self.fields[field.name] = None
        # Add field to ordered list for packing/unpacking
        self.field_list.append(field)

    def unpack(self):
        #print('unpacking from data')
        #print(f'data {self.data}')

        fmt_string = '<'    # All data is little endian
        for f in self.field_list:
            # print(f.name, f.pack)
            fmt_string += f.pack

        #print(fmt_string)
        #print(fmt_string, struct.calcsize(fmt_string))

        results = struct.unpack(fmt_string, self.data)
        #print(results)

        i = 0
        for f in self.field_list:
            value = results[i]
            #print(f'{f.name}: {value}')
            self.fields[f.name] = results[i]
            i += 1

    def pack(self):
        #print('packing')
        #print(f'data {self.data}')

        fmt_string = '<'    # All data is little endian
        for f in self.field_list:
            #print(f.name, f.pack)
            fmt_string += f.pack

        #print(fmt_string)
        #print(fmt_string, struct.calcsize(fmt_string))

        fields = ()
        for f in self.field_list:
            value = self.fields[f.name]
            #print(f'{f.name}: {value}')
            fields += (value, )

        data = struct.pack(fmt_string, *fields)
        # print(data)
        self.data = data

    def names(self):
        [print(a.name) for a in self.field_list]

    def __setattr__(self, name, value):
        """
        Overload to allow direct access to fields
        """
        if name[0:2] == 'f_':
            print(f'*** setting field {name}, {value}')
            self.fields[name[2:]] = value
        else:
            return super().__setattr__(name, value)

    def __getattribute__(self, name):
        """
        Overload to allow direct access to fields
        """
        if name[0:2] == 'f_':
            value = self.fields[name[2:]]
            print(f'*** getting field {name} -> {value}')
            return value
        else:
            return super().__getattribute__(name)

    def __str__(self):
        res = f'{self.NAME} {self.CID}'
        # res = f'{self.NAME} cls:{self.cls:02x} id:{self.id:02x} len:{self.length}'
        for f in self.field_list:
            res += f'\n  {f.name}: {self.fields[f.name]}'

        return res


class UbxPoll(UbxFrame):
    """
    Base class for a polling frame.

    Create by specifying u-blox message class and id.
    """
    def __init__(self):
        super().__init__()


class UbxAckAck(UbxFrame):
    CID = UbxCID(0x05, 0x01)
    NAME = 'UBX-ACK-ACK'

    def __init__(self):
        super().__init__()
