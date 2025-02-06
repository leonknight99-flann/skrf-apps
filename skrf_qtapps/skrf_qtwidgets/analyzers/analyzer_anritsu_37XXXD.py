import skrf as rf

from skrf.vi.vna.vna import VNA


class Analyzer(VNA):
    DEFAULT_VISA_ADDRESS = "GPIB0::6::INSTR"
    NAME = "Anritsu 37369D"
    NPORTS = 2
    NCHANNELS = 1
    SCPI_VERSION_TESTED = ''

    def __init__(self, address : str, backend : str = "@py", **kwargs):
        super().__init__(address, backend, **kwargs)

        self._resource.timeout = 10_000


    def get_snp_network(self, ports, **kwargs):
        ''' MAIN METHOD for obtaining S parameters, like get_snp_network((1,)) or get_snp_network((1,2)). '''
        ports = tuple(ports)
        
        self.write("TRS;WFS;")

        if ports==(1,):
            return self.one_port('S11')
        elif ports==(2,):
            return self.one_port('S22')
        elif ports==(1,2) or ports==(2,1):
            return self.two_port()
        else:
            raise(ValueError("Invalid ports "+str(ports)+". Options: (1,) (2,) (1,2)."))
        

    def one_port(self, s_param):
        ''' MAIN METHOD for obtaining S parameters for one-port devices. '''
        if s_param == 'S11':
            ntwk = rf.Network()
            freq = self.write("OFV;")  # Output Frequency Value
            s11 = self.write("OS11C;")  # Output S11 Corrected
            print(f'{freq} {s11}')
            self.write("RTL;")  # Return To Local
            return ntwk
        elif s_param == 'S22':
            ntwk = rf.Network()
            freq = self.write("OFV;")  # Output Frequency Value
            s22 = self.write("OS22C;")  # Output S22 Corrected
            print(f'{freq} {s22}')
            self.write("RTL;")  # Return To Local
            return ntwk
        else:
            self.write("RTL;")  # Return To Local
            raise(ValueError("Invalid s_param "+s_param+". Options: 'S11' 'S22'."))
        


    def two_port(self):
        ''' MAIN METHOD for obtaining S parameters for two-port devices. '''
        ntwk = rf.Network()
        freq = self.write("OFV;")
        s = self.write("O4SC;")  # Output 4 S-Parameters Corrected
        print(f'{freq} {s}')
        self.write("RTL;")  # Return To Local
        return ntwk

