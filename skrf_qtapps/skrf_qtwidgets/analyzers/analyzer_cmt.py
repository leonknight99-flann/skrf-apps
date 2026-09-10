from skrf.vi.vna.copper_mountain import CMT


class Analyzer(CMT):
    DEFAULT_VISA_ADDRESS = 'TCPIP0::127.0.0.1::5025::SOCKET'
    NAME = "CMT C4220"
    NPORTS = 2
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''
