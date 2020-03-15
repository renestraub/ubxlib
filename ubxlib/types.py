# import logging
import struct


# logger = logging.getLogger('gnss_tool')


class Items(object):
    def __init__(self):
        self.order = -1
        self.value = None

    def __str__(self):
        return f'{self.name}: {self.value}'


class U1(Items):
    pack = 'B'

    def __init__(self, name):
        super().__init__()
        self.name = name


class I2(Items):
    pack = 'h'

    def __init__(self, name):
        super().__init__()
        self.name = name


class I4(Items):
    pack = 'I'

    def __init__(self, name):
        super().__init__()
        self.name = name


class X4(Items):
    pack = 'I'

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
        #print('unpacking from data')
        #print(f'data {self.data}')

        fmt_string = '<'    # All data is little endian

        for (k, v) in sorted(self._fields.items(), key=lambda item: item[1].order):
            # print(f.name, f.pack)
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

    def pack(self):
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
        if('_fields' in self.__dict__ and name in self.__dict__['_fields']):
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
            res += f'\n  {v}'

        return res
