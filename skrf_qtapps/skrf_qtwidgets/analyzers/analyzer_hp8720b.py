from skrf.vi.vna.hp import hp8720b


class Analyzer(hp8720b.HP8720B):
    DEFAULT_VISA_ADDRESS = "GPIB::16::INSTR"
    NAME = "HP 8720B"
    NPORTS = 2
    NCHANNELS = 2
    SCPI_VERSION_TESTED = ''
