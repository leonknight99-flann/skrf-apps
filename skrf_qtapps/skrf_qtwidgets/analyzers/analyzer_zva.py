from skrf.vi.vna.rohde_schwarz import ZVA


class Analyzer(ZVA):
    DEFAULT_VISA_ADDRESS = "GPIB0::20::INSTR"
    NAME = "ZVA 50"
    NPORTS = 4
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''
