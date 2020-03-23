import struct


class Item(object):
    def __init__(self, value=None):
        self.order = -1
        self.value = value

    def pack(self):
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
        return f'{self.name}: {self.value}'


class Padding(Item):
    def __init__(self, length, name):
        super().__init__(value=0)
        self.name = name
        self.length = length

    def pack(self):
        """
        Dedicated unpack method for padding bytes

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
        super().__init__(value='')
        self.name = name
        self.length = length

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
        super().__init__(value=0)
        self.name = name


class I2(Item):
    fmt = 'h'

    def __init__(self, name):
        super().__init__()
        # TODO: Mave name to base class, provide via ctor
        self.name = name


class I4(Item):
    fmt = 'I'

    def __init__(self, name):
        super().__init__()
        self.name = name


class X4(Item):
    fmt = 'I'

    def __init__(self, name):
        super().__init__()
        self.name = name


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

    """
    def unpack2(self, data):
        #print('unpacking from data')
        print(f'data {data}')

        fmt_string = '<'    # All data is little endian

        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            # print(v.name, v.pack)
            fmt_string += v.pack

        # print(fmt_string, struct.calcsize(fmt_string))
        results = struct.unpack(fmt_string, data)
        # print(results)

        i = 0
        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            value = results[i]
            # print(f'{f.name}: {value}')
            self._fields[k].value = results[i]
            i += 1
    """

    def pack(self):
        work_data = bytearray()
        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            # print(f'packing {k} {v.value} {type(v)} {v.pack}')
            work_data += v.pack()

        return work_data

    """
    def pack2(self):
        print('packing')

        fields = ()
        fmt_string = '<'    # All data is little endian

        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            # print(v.name, v.pack)
            fmt_string += v.pack
            # print(f'{v.name}: {v.value}')
            fields += (v.value, )

        # print(fmt_string, struct.calcsize(fmt_string))

        data = struct.pack(fmt_string, *fields)
        # print(data)

        return data
    """

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
