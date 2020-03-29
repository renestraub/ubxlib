

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
        # print(f'frame factory register {self.__instance}')
        # print(frame_class)
        # print(frame_class.CID)
        x = frame_class()
        # print(x)
        self.__frames[frame_class.CID] = frame_class
        # print(self.__frames)

    def build(self, cid):
        """
        Constructs an empty frame of the desired type
        """
        frame_type = self.__frames[cid]
        # print(frame_type)
        frame = frame_type()
        return frame

    def build_with_data(self, cid, data):
        """
        Constructs the desired frame and fills it with provided data
        """
        frame_type = self.__frames[cid]
        frame = frame_type.construct(data)
        return frame
