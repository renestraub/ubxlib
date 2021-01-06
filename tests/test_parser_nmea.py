from ubxlib.parser_nmea import NmeaParser


class TestParserNmea:
    def test_to_bin(self):
        assert NmeaParser._to_bin('0') == 0
        assert NmeaParser._to_bin('9') == 9
        assert NmeaParser._to_bin('a') == 10
        assert NmeaParser._to_bin('A') == 10
        assert NmeaParser._to_bin('f') == 15
        assert NmeaParser._to_bin('F') == 15

        assert NmeaParser._to_bin('g') == -1
        assert NmeaParser._to_bin('G') == -1
        assert NmeaParser._to_bin('$') == -1

    def test_ok(self):
        data = bytes("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A".encode())
        uut = NmeaParser()
        assert uut.frames_rx == 0
        uut.process(data)
        assert uut.frames_rx == 1

    def test_wrong_checksum(self):
        data = bytes("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6B".encode())
        uut = NmeaParser()
        uut.process(data)
        assert uut.frames_rx == 0

    def test_checksum_missing(self):
        data_fail = bytes("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W".encode())
        data = bytes("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A".encode())
        uut = NmeaParser()
        uut.process(data_fail)
        assert uut.frames_rx == 0

        uut.process(data)
        assert uut.frames_rx == 1

    def test_checksum_invalid_chars(self):
        data1 = bytes("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*xx".encode())
        uut = NmeaParser()
        uut.process(data1)
        assert uut.frames_rx == 0

        data2 = bytes("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*0g".encode())
        uut = NmeaParser()
        uut.process(data2)
        assert uut.frames_rx == 0
