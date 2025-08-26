from skrf.vi.vna.anritsu import L37XXXD


class Analyzer(L37XXXD):
    DEFAULT_VISA_ADDRESS = "GPIB0::6::INSTR"
    NAME = "Anritsu 37369D"
    NPORTS = 2
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''
