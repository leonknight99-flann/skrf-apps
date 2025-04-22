import pyodbc
import skrf as rf
import numpy as np

allowed_flann_refs = {1: ['MWV-001','MWV-004','MWV-059'], 
                      2: ['MWV-005','MWV-069','MWV-052','MWV-053','MWV-054'], 
                      3: ['MWV-014','MWV-017','MWV-018','MWV-024','MWV-027','MWV-040'], 
                      4: ['MWV-055','MWV-056','MWV-031']}

def get_specification_network(Instrument_ID_list: list):
    allowed_spec = [value for key, value in iter(allowed_flann_refs.items())]
    allowed_spec = [item for sublist in allowed_spec for item in sublist]  # Flatten the list of lists
    list_spec_ntwk = []
    for instrument_ID in Instrument_ID_list:
        # print(f'\nInstrument ID: {instrument_ID}')
        spec_dict = {}
        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        for row in mydb_cursor.execute("select Flann_Ref, Instrument_Number, Instrument_ID, NumNom, NumLwr, NumUpr, SpecDetail_ID, SpecDetail_Link from qry_InstrumentParameter_Search where (Flann_Ref like '%MWV%') and (Instrument_ID = ?)",(instrument_ID)):
            if row.Flann_Ref in allowed_spec:
                spec_dict[row.Flann_Ref] = [row.NumNom,row.NumLwr,row.NumUpr,row.Instrument_Number,row.SpecDetail_ID,row.SpecDetail_Link]
        mydb.close()

        instrument_flann_refs = list(spec_dict.keys())
        # print(f'Found specifications: {instrument_flann_refs}')
        number_of_ports = max([key for key, value in allowed_flann_refs.items() if any(flann_ref in value for flann_ref in instrument_flann_refs)])
        # print(f'Port count: {number_of_ports}')

        try:  # To create a specification network from found ISM parameters - Currently for 2 or 1 port devices
            s_matrix = np.zeros((2, number_of_ports, number_of_ports), dtype=complex)
            
            for i in range(number_of_ports):
                for j in range(number_of_ports):                    
                    if i == j and 'MWV-004' in spec_dict:  # VSWR
                        s_matrix[:,i,j] = (abs(float(spec_dict['MWV-004'][0])) - 1) / (abs(float(spec_dict['MWV-004'][0])) + 1)
                    elif all([i==j, bool(any([i==0,i==1])), 'MWV-017' in spec_dict]):  # Primary Arm VSWR Coupler
                        s_matrix[:,i,j] = (abs(float(spec_dict['MWV-017'][0])) - 1) / (abs(float(spec_dict['MWV-017'][0])) + 1)
                    elif all([i==j, i==2, 'MWV-018' in spec_dict]):  # Secondary Arm VSWR Coupler
                        s_matrix[:,i,j] = (abs(float(spec_dict['MWV-018'][0])) - 1) / (abs(float(spec_dict['MWV-018'][0])) + 1)
                    elif i == j and 'MWV-059' in spec_dict:  # Return Loss
                        s_matrix[:,i,j] = 10 ** (- abs(float(spec_dict['MWV-059'][0])) / 20)
                    elif any([bool(i+j==1 and 'MWV-005' in spec_dict), bool(i+j==5 and 'MWV-005' in spec_dict)]):  # Insertion Loss
                        s_matrix[:,i,j] = 10 ** (- abs(float(spec_dict['MWV-005'][0])) / 20)
                    elif all([i!=j, i+j==2,'MWV-024' in spec_dict]):  # Coupling - 3 port Couplers ONLY
                        s_matrix[:,i,j] = 10 ** (- abs(float(spec_dict['MWV-024'][0])) / 20)
                    elif all([i!=j, i+j==3,'MWV-014' in spec_dict]):  # Directivity - 3 port Couplers ONLY
                        s_matrix[:,i,j] = 10 ** (- abs(float(spec_dict['MWV-014'][0])) / 20)
                    elif all([i!=j, i+j==1, 'MWV-069' in spec_dict]):  # Nominal Attenuation
                        s_matrix[:,i,j] = 10 ** (- abs(float(spec_dict['MWV-069'][0])) / 20)

            if 'MWV-001' in spec_dict:
                freq = rf.Frequency.from_f([spec_dict['MWV-001'][1], spec_dict['MWV-001'][2]], unit='Hz')
            elif 'MWV-052' in spec_dict:
                freq = rf.Frequency.from_f([spec_dict['MWV-052'][1], spec_dict['MWV-052'][2]], unit='Hz')
            
            spec_ntwk = rf.Network(frequency=freq, s=s_matrix, name=f'Specification {next(iter(spec_dict.values()))[3]}')
            print(spec_ntwk)
            list_spec_ntwk.append(spec_ntwk)
        except Exception:
            print(f'Error creating specification network for Instrument ID: {instrument_ID}')
            pass
        

    if len(list_spec_ntwk) == 1:
        return list_spec_ntwk[0]
    return list_spec_ntwk


# print(get_specification_network([16010,17404,215]))