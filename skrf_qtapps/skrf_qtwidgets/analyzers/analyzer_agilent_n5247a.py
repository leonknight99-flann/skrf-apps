from skrf.vi.vna.keysight import pna


class Analyzer(pna.PNA):
    DEFAULT_VISA_ADDRESS = "GPIB::16::INSTR"
    NAME = "Agilent N5247A"
    NPORTS = 4
    NCHANNELS = 32
    SCPI_VERSION_TESTED = 'A.09.80.20'
