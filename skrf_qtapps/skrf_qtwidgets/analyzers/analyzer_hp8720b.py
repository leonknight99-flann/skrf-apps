from skrf.vi.vna.hp import HP8720B


class Analyzer(HP8720B):
    DEFAULT_VISA_ADDRESS = "GPIB::16::INSTR"
    NAME = "HP 8720B"
    NPORTS = 2
    NCHANNELS = 2
    SCPI_VERSION_TESTED = ''

    def __init__(self, port1, port2, sweep_new, channel, raw_data, **kwargs):

        self.port1 = port1
        self.port2 = port2
        self.sweep_new = sweep_new
        self.channel = channel
        self.raw_data = raw_data
    
    def set_measurement_parameters(self):
        return




