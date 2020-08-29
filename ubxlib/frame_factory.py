import logging

logger = logging.getLogger('gnss_tool')


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
        """
        Registers a UXB frame class

        You have to register all frames classes that you expect to receive.
        The ubx servers require these prototypes to build the correct ubx frames.

        Notes:
        - Register each frame class only once
        - Register the prototype class not instances (objects)
        """
        # Class shall be registered not instances
        if not isinstance(frame_class, type):
            raise Exception("Can only register classes not instances (objects)")

        # Registering the same frame class multiple times is considered
        # bad style. For now we just ignore the call. Future versions
        # will assert.
        if frame_class.CID in self.__frames:
            logger.warning(f'trying to register {frame_class} multiple times')
            logger.warning(f'future releases will throw an Exception')
            return

        self.__frames[frame_class.CID] = frame_class

    def build(self, cid):
        """
        Constructs an empty frame of the desired type

        Will throw KeyError if frame class is not known
        """
        frame_class = self.__frames[cid]
        frame = frame_class()
        return frame

    def build_with_data(self, cid, data):
        """
        Constructs the desired frame and fills it with provided data

        Will throw KeyError if frame class is not known
        """
        frame_class = self.__frames[cid]
        frame = frame_class.construct(data)
        return frame
