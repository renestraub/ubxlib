

class FrameFactory(object):
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if not FrameFactory.__instance:
            FrameFactory()

        return FrameFactory.__instance

    @staticmethod
    def destroy():
        FrameFactory.__instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if FrameFactory.__instance:
            raise Exception("This class is a singleton!")
        else:
            FrameFactory.__instance = self

        super().__init__()
        self.__frames = dict()

    def register(self, frame_class):
        x = frame_class()

        # Registering the same frame class multiple times is considered
        # bad style. For now we just ignore the call. Future versions
        # will assert.
        if frame_class.CID in self.__frames:
            # assert False
            return

        self.__frames[frame_class.CID] = frame_class

    def build(self, cid):
        """
        Constructs an empty frame of the desired type
        """
        frame_type = self.__frames[cid]
        frame = frame_type()
        return frame

    def build_with_data(self, cid, data):
        """
        Constructs the desired frame and fills it with provided data
        """
        frame_type = self.__frames[cid]
        frame = frame_type.construct(data)
        return frame
