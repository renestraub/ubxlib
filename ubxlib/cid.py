
class UbxCID(object):
    def __init__(self, cls, id):
        super().__init__()
        self.__cls = cls
        self.__id = id

    @property
    def cls(self):
        return self.__cls

    @property
    def id(self):
        return self.__id

    def __eq__(self, other):
        return self.__cls == other.__cls and self.__id == other.__id

    def __str__(self):
        return f'cls:{self.__cls:02x} id:{self.__id:02x}'

    def __hash__(self):
        return hash((self.__cls, self.__id))
