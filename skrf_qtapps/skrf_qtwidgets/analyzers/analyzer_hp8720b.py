from skrf.vi.vna.hp import HP8720B


class Analyzer(HP8720B):
    DEFAULT_VISA_ADDRESS = "GPIB0::16::INSTR"
    NAME = "HP 8720B"
    NPORTS = 2
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''


    # def get_snp_network(self, ports, **kwargs):
    #     print(ports)
    #     network = super().get_snp_network(ports, **kwargs)
    #     return network # super().get_snp_network(ports, **kwargs)

