import pyodbc
import skrf as rf
import numpy as np

def get_specification_network(Instrument_ID_list: list):
    allowed_spec = ['MWV-001', 'MWV-004', 'MWV-005', 'MWV-052', 'MWV-059']  # Currently supports Frequency Band, VSWR, IL, RL, and Passband - Requires a conversion layer for other ISM parameters
    list_spec_ntwk = []
    for instrument_ID in Instrument_ID_list:
        spec_list = []
        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        for row in mydb_cursor.execute("select Flann_Ref, Instrument_Number, Instrument_ID, NumNom, NumLwr, NumUpr from qry_InstrumentParameter_Search where (Flann_Ref like '%MWV%') and (Instrument_ID = ?)",(instrument_ID)):
            if row.Flann_Ref in allowed_spec:
                spec_list.append([row.Flann_Ref,row.NumNom,row.NumLwr,row.NumUpr,row.Instrument_Number])
        mydb.close()
        try:  # To create a specification network from found ISM parameters - Currently for 2 or 1 port devices
            s11, s21 = 0, 0
            for s in range(len(spec_list)):
                if spec_list[s][0] == 'MWV-052' or spec_list[s][0] == 'MWV-001':
                    freq = rf.Frequency.from_f([spec_list[s][2], spec_list[s][3]], unit='Hz')
                elif spec_list[s][0] == 'MWV-004':
                    s11 = (abs(float(spec_list[s][1])) - 1) / (abs(float(spec_list[s][1])) + 1)
                elif spec_list[s][0] == 'MWV-059':
                    s11 = 10 ** (- abs(float(spec_list[s][1])) / 20)
                elif spec_list[s][0] == 'MWV-005':
                    s21 = 10 ** (- abs(float(spec_list[s][1])) / 20)
            s_matrix = np.zeros((2, 2, 2), dtype=complex)
            s_matrix[:, 0, 0] = s11
            s_matrix[:, 1, 0] = s21
            s_matrix[:, 0, 1] = s21
            s_matrix[:, 1, 1] = s11
            spec_ntwk = rf.Network(frequency=freq, s=s_matrix, name=f'Specification {spec_list[0][4]}')
        except Exception:
            return None
        list_spec_ntwk.append(spec_ntwk)

    if len(list_spec_ntwk) == 1:
        return list_spec_ntwk[0]
    return list_spec_ntwk