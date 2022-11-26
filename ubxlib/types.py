import struct


class Item(object):
    fmt = ''

    def __init__(self, name, value=None):
        self.order = -1
        self.name = name
        self.value = value

    def pack(self):
        """
        Returns packed value

        @return: bytearray with value packed as defined by type
        """
        fmt_string = '<' + self.fmt    # use little endian mode
        data = struct.pack(fmt_string, self.value)
        return data

    def unpack(self, data):
        """
        Unpacks value, whose type is defined by class

        @param data: bytearray to extract data from
        @return: number of bytes consumed
        """
        fmt_string = '<' + self.fmt    # use little endian mode
        length = struct.calcsize(fmt_string)
        results = struct.unpack(fmt_string, data[:length])
        self.value = results[0]
        return length

    def __str__(self):
        if hasattr(self, 'fmt_string'):
            return f'{self.name}: {self.value:{self.fmt_string}}'
        else:
            return f'{self.name}: {self.value}'


class Padding(Item):
    def __init__(self, length, name):
        super().__init__(name, value=0)
        self.length = length

    def pack(self):
        """
        Dedicated pack method for padding bytes

        Inserts 0x00 padding bytes
        """
        return bytearray(b'\x00') * self.length

    def unpack(self, data):
        """
        Dedicated unpack method for padding bytes

        Just advances in data buffer
        """
        return self.length


class CH(Item):
    def __init__(self, length, name):
        super().__init__(name, value='')
        self.length = length

    def pack(self):
        """
        Dedicated pack method for fixed-sized strings

        Inserts 0x00 padding bytes if required
        """
        data = self.value.encode()
        if len(data) < self.length:
            data = data + bytes(self.length - len(data))
        elif len(data) > self.length:
            raise ValueError

        return data[0:self.length]

    def unpack(self, data):
        """
        Dedicated unpack method for fixed-sized strings

        Extracts ISO 8859-1 text directly from data and converts it
        to Python string (Unicode). Trailing zeroes (padding) at end
        of string are removed.
        Advances buffer by fixed size of text.
        """
        # Check that we have enough payload to process
        if len(data) < self.length:
            raise ValueError

        # Check string is valid, for simplicty raise ValueError so caller
        # does not need to know about Unicode conversion
        raw_text = data[:self.length]
        try:
            text = raw_text.decode()
        except UnicodeDecodeError:
            raise ValueError

        # Remove trailing termination characters (0x00)
        text = text.rstrip('\x00')
        self.value = text

        return self.length


class U1(Item):
    fmt = 'B'

    def __init__(self, name):
        super().__init__(name, value=0)


class U2(Item):
    fmt = 'H'

    def __init__(self, name):
        super().__init__(name, value=0)


class U4(Item):
    fmt = 'I'

    def __init__(self, name):
        super().__init__(name, value=0)


class I1(Item):
    fmt = 'b'

    def __init__(self, name):
        super().__init__(name, value=0)


class I2(Item):
    fmt = 'h'

    def __init__(self, name):
        super().__init__(name, value=0)


class I4(Item):
    fmt = 'i'

    def __init__(self, name):
        super().__init__(name, value=0)


class X1(Item):
    fmt = 'B'
    fmt_string = '02x'

    def __init__(self, name):
        super().__init__(name, value=0)


class X2(Item):
    fmt = 'H'
    fmt_string = '04x'

    def __init__(self, name):
        super().__init__(name, value=0)


class X4(Item):
    fmt = 'I'
    fmt_string = '08x'

    def __init__(self, name):
        super().__init__(name, value=0)


class CfgKeyData(Item):
    def __init__(self, name):
        super().__init__(name)
        self.value = None
        # self.data = None
        self.group_id = None
        self.item_id = None

    def unpack(self, data):
        """
        Unpacks configuration item key and data
        - Data length is dynamic and depends on key[30..28], invalid length raise ValueError

        @param data: bytearray to extract data from
        @return: number of bytes consumed
        """
        if len(data) < 4:
            raise ValueError

        # TODO: Simplify by hardcoding lengths, fmt string
        fmt_string = '<I'    # extract 32 bits in little endian mode
        length = struct.calcsize(fmt_string)    # should always be 4
        results = struct.unpack(fmt_string, data[:length])
        header = results[0]
        data = data[length:]
        bytes_consumed = length

        size = (header >> 28) & 0x7
        self.group_id = (header >> 16) & 0xFF
        self.item_id = (header >> 0) & 0xFFF

        num_bits = [0, 1, 8, 16, 32, 64, 0, 0]
        self.bits = num_bits[size]

        size_names = ['<inv>', 'one bit', 'one byte', 'two bytes', 'four bytes', 'eight bytes', '<inv>', '<inv>']
        self.size_name = size_names[size]

        try:
            if self.bits == 32:
                results = struct.unpack("<I", data[:4])
                self.value = results[0]
                data = data[4:]
                bytes_consumed += 4
            elif self.bits == 16:
                results = struct.unpack("<H", data[:2])
                self.value = results[0]
                data = data[2:]
                bytes_consumed += 2
            elif self.bits == 8:
                results = struct.unpack("<B", data[:1])
                self.value = results[0]
                data = data[1:]
                bytes_consumed += 1
            elif self.bits == 1:
                results = struct.unpack("<B", data[:1])
                if results[0] == 0:
                    self.value = False
                elif results[0] == 1:
                    self.value = True
                else:
                    raise ValueError
                bytes_consumed += 1
            elif self.bits == 64:
                results = struct.unpack("<Q", data[:8])
                self.value = results[0]
                data = data[8:]
                bytes_consumed += 8
            else:
                raise ValueError
        except struct.error:
            raise ValueError

        return bytes_consumed

    def __str__(self):
        res = self.name + ': '
        res += f'group: 0x{self.group_id:02x}'
        res += f', item: 0x{self.item_id:03x}'
        res += f', bits: {self.bits}'
        res += f', value: 0x{self.value:x}'
        return res


class Fields(object):
    def __init__(self):
        super().__init__()
        self._fields = dict()
        self._next = 0

    def add(self, field):
        # Insert order (1, 2, 3, ..) in Item object, so that we can later
        # pack/unpack in correct order
        field.order = self.next_ord()

        # Create named entry in dictionary for value
        if field.name not in self._fields:
            self._fields[field.name] = field
        else:
            raise KeyError

    def get(self, field):
        return self._fields[field]

    def unpack(self, data):
        work_data = data
        for (_, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            consumed = v.unpack(work_data)
            work_data = work_data[consumed:]

        return work_data

    def pack(self):
        work_data = bytearray()
        for (_, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            work_data += v.pack()

        return work_data

    def next_ord(self):
        ret = self._next
        self._next += 1
        return ret

    def __setattr__(self, name, value):
        """
        Overload to allow direct access to fields

        If variable <name> is found in _fields set its value
        """
        if '_fields' in self.__dict__ and name in self.__dict__['_fields']:
            self.__dict__['_fields'][name].value = value
        else:
            return super().__setattr__(name, value)

    def __getattribute__(self, name):
        """
        Overload to allow direct access to field entries
        """
        obj_dict = object.__getattribute__(self, '__dict__')
        if '_fields' in obj_dict:
            _fields = object.__getattribute__(self, '_fields')
            if name in _fields:
                value = _fields[name].value
                return value

        return super().__getattribute__(name)

    def __str__(self):
        res = ''
        for (_, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            if not isinstance(v, Padding):
                res += f'\n  {v}'

        return res
