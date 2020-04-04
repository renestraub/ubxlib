import struct


class Item(object):
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
        # print(f'unpacking {length}')
        results = struct.unpack(fmt_string, data[:length])
        # print(results[0])
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

        Inserts 0x00 padding bytes
        """
        data = self.value.encode()
        # TODO: Fill up string with 0es when shorter than field
        return data[0:self.length]

    def unpack(self, data):
        """
        Dedicated unpack method for fixed-sized strings

        Extracts ISO 8859-1 text directly from data and converts it
        to Python string (Unicode).
        Advances buffer by fixed size of text.
        """
        # TODO: Length check
        # print(f"unpacking {self.length} from {data}")
        raw_text = data[:self.length]
        # TODO: Decoder error check
        text = raw_text.decode()
        # print(text)
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
        self._fields[field.name] = field

    def unpack(self, data):
        # print('unpacking from data')
        # print(f'data {data}')

        work_data = data
        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            # print(f'data {work_data}')
            consumed = v.unpack(work_data)
            work_data = work_data[consumed:]

        return work_data

    def pack(self):
        work_data = bytearray()
        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            # print(f'packing {k} {v.value} {type(v)} {v.pack}')
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
        # print(f'*** setting field {name}, {value}')
        if '_fields' in self.__dict__ and name in self.__dict__['_fields']:
            self.__dict__['_fields'][name].value = value
        else:
            return super().__setattr__(name, value)

    def __getattribute__(self, name):
        """
        Overload to allow direct access to field entries
        """
        # print(f'*** getting field {name}')
        obj_dict = object.__getattribute__(self, '__dict__')
        if '_fields' in obj_dict:
            _fields = object.__getattribute__(self, '_fields')
            # print(_fields)
            if name in _fields:
                # print(f'found {name}')
                value = _fields[name].value
                return value

        return super().__getattribute__(name)

    def __str__(self):
        res = ''
        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            if not isinstance(v, Padding):
                res += f'\n  {v}'

        return res
