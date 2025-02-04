from skrf.vi.vna.vna import VNA


class Analyzer(VNA):
    DEFAULT_VISA_ADDRESS = "GPIB::16::INSTR"
    NAME = "Anritsu 37369D"
    NPORTS = 2
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''