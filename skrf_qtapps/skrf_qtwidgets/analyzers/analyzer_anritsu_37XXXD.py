from skrf.vi.vna.vna import VNA


class Analyzer(VNA):
    DEFAULT_VISA_ADDRESS = "GPIB0::6::INSTR"
    NAME = "Anritsu 37369D"
    NPORTS = 2
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''

    def __init__(self, address : str, backend : str = "@py", **kwargs):
        super().__init__(address, backend, **kwargs)


    def get_snp_network(self, ports, **kwargs):
        ''' MAIN METHOD for obtaining S parameters, like get_snp_network((1,)) or get_snp_network((1,2)). '''
        ports = tuple(ports)
        sweep = kwargs.get("sweep", True)

        if ports==(1,):
            self.write('S11;')
            return self.one_port(fresh_sweep=sweep)
        elif ports==(2,):
            self.write('S22;')
            return self.one_port(fresh_sweep=sweep)
        elif ports==(1,2) or ports==(2,1):
            return self.two_port(fresh_sweep=sweep)
        else:
            raise(ValueError("Invalid ports "+str(ports)+". Options: (1,) (2,) (1,2)."))
