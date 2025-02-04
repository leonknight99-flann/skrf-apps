import os
import re
import skrf
import numpy as np
import pyodbc
from collections import OrderedDict

import matplotlib.pyplot as plt

from qtpy import QtCore, QtWidgets

from . import widgets
from .networkPlotWidget import NetworkPlotWidget
from .analyzers import analyzers

testDataPath = '\\\\Filesrv\\Test\\RFData\\'


class NetworkCreateWidget(QtWidgets.QWidget):
    item_removed = QtCore.Signal()
    item_updated = QtCore.Signal(object)
    save_single_requested = QtCore.Signal(object, str)
    selection_changed = QtCore.Signal(object)
    same_item_clicked = QtCore.Signal(object)
    state_changed = QtCore.Signal()

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        self.Instrument_ID = None
        self.ntwk = None
        self.spec_ntwk = None

        self.verticalLayout_main = QtWidgets.QVBoxLayout(self)  # Primary Widget Layout
        self.verticalLayout_main.setContentsMargins(0, 0, 0, 0)

        self.analyserLabel = QtWidgets.QLabel("Analyser:") # Row1
        self.analyserComboBox = QtWidgets.QComboBox()
        self.analyserAddressLabel = QtWidgets.QLabel("Address:")
        self.analyserAddress = QtWidgets.QLineEdit()
        self.analyserAddress.setPlaceholderText("VISA String")

        self.analyserComboBox.currentIndexChanged.connect(self.update_selected_analyzer)
        for key in analyzers.keys():
            self.analyserComboBox.addItem(key)

        self.openButton = QtWidgets.QPushButton("Open Network")
        self.openButton.released.connect(self.load_from_files)
        self.openButton.setDisabled(True)  # Remove once the feature has been added

        self.captureButton = QtWidgets.QPushButton("Capture Data")
        self.captureButton.clicked.connect(lambda: self.capture_data())

        self.importButton = QtWidgets.QPushButton("Import Captured Data")
        self.importButton.setDisabled(True)

        self.partidLabel = QtWidgets.QLabel("Part ID:") # Row2
        self.partid = QtWidgets.QLineEdit()
        self.partid.setPlaceholderText("Part ID or Test Data Folder Name")
        self.instrumentNumberInfoDict = {}
        self.partid.textChanged.connect(self.get_instument_number)

        self.specInstrumentNumber = QtWidgets.QLineEdit()
        self.specInstrumentNumber.setPlaceholderText("Spec. Instrument Number")
        self.specInstrumentNumber.setReadOnly(True)

        self.serialNumber = QtWidgets.QLineEdit()
        self.serialNumber.setPlaceholderText("Serial Number")

        self.notesTextBox = QtWidgets.QPlainTextEdit()
        self.notesTextBox.setPlaceholderText("Notes")
        
        self.operatorNumberLabel = QtWidgets.QLabel("Operator:") # Row-1
        self.operatorNumber = QtWidgets.QSpinBox()
        self.operatorNumber.setMinimum(1)
        self.operatorNumber.setMaximum(999)
        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(lambda: self.save_network_item())

        self.s_paramButtons = {}

        self.s_paramLayout = QtWidgets.QGridLayout()
        self.s_paramGroup = QtWidgets.QButtonGroup()
        
        for i in range(4):
            for j in range(4):
                button = QtWidgets.QRadioButton(f'S{i+1}{j+1}')
                if i + j > 1 and not (i==1 and j==1):
                    button.setDisabled(True)  # Remove once the feature has been added
                self.s_paramLayout.addWidget(button, i, j)
                self.s_paramGroup.addButton(button, id=(j+4*i))  # Button ids are 0-15 for S11,S12,S13,...,S44
        self.s_paramGroup.setExclusive(False)

        self.row1 = QtWidgets.QHBoxLayout() # Row1
        self.row1.addWidget(self.analyserLabel)
        self.row1.addWidget(self.analyserComboBox)
        self.row1.addWidget(self.analyserAddressLabel)
        self.row1.addWidget(self.analyserAddress)

        self.row2 = QtWidgets.QHBoxLayout() # Row2
        self.row2.addWidget(self.partidLabel)
        self.row2.addWidget(self.partid)

        self.rowFinal = QtWidgets.QHBoxLayout() # Row-1
        self.rowFinal.addWidget(self.operatorNumberLabel)
        self.rowFinal.addWidget(self.operatorNumber)
        self.rowFinal.addWidget(self.openButton)
        self.rowFinal.addWidget(self.saveButton)

        self.verticalLayout_main.addLayout(self.row1)
        self.verticalLayout_main.addWidget(self.captureButton)
        self.verticalLayout_main.addLayout(self.s_paramLayout)
        self.verticalLayout_main.addWidget(self.importButton)
        self.verticalLayout_main.addLayout(self.row2)
        self.verticalLayout_main.addWidget(self.specInstrumentNumber)
        self.verticalLayout_main.addWidget(self.serialNumber)
        self.verticalLayout_main.addWidget(self.notesTextBox)

        self.verticalLayout_main.addLayout(self.rowFinal)   

    def update_selected_analyzer(self):
        cls = analyzers[self.analyserComboBox.currentText()]
        self.analyserAddress.setText(cls.DEFAULT_VISA_ADDRESS)

    def get_analyzer_network(self, ports):
        nwa = None
        try:
            nwa = analyzers[self.analyserComboBox.currentText()](self.analyserAddress.text())
        except Exception:
            print('Unable to get analyzer')
        
        ntwk = nwa.get_snp_network(ports)
        print(ntwk)
        return ntwk
    
    def load_networks(self, ntwks):
        if not ntwks:
            return
        
    def load_from_files(self, caption="load touchstone file"):
        self.load_networks(widgets.load_network_files(caption))

    @property
    def ntwk_plot(self):
        return self._ntwk_plot  # type: NetworkPlotWidget

    @ntwk_plot.setter
    def ntwk_plot(self, ntwk_plot):
        if isinstance(ntwk_plot, NetworkPlotWidget):
            self._ntwk_plot = ntwk_plot
            self.item_removed.connect(self._ntwk_plot.clear_plot)
        else:
            self._ntwk_plot = None

    def capture_data(self):
        if not self.ntwk_plot:
            return
        ntwk_list = []
        self.ntwk = None
        checked_buttons = [i for i, button in enumerate(self.s_paramGroup.buttons()) if button.isChecked()] # Checked buttons are 0-15, i%4 is the column, i//4 is the row
        print(checked_buttons)
        if checked_buttons == [0]:
            self.ntwk = self.get_analyzer_network((1,))
        elif checked_buttons == [5]:
            self.ntwk = self.get_analyzer_network((2,))
        else:
            self.ntwk = self.get_analyzer_network((1,2))
        if self.serialNumber.text():
            self.ntwk.name = self.serialNumber.text()
        
        # self.ntwk = skrf.Network('test.s2p')
        ntwk_list.append(self.ntwk)

        if self.spec_ntwk is not None:
            ntwk_list.append(self.spec_ntwk)

        if ntwk_list:
            ntwk_with_spec = ntwk_list if len(ntwk_list) > 1 else ntwk_list[0]
        
        self.ntwk_plot.set_networks(ntwk_with_spec)

    def get_instument_number(self):
        self.instrumentNumberInfoDict.clear()
        self.partid.setText(self.partid.text().upper())
        partid = self.partid.text()
        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        partid_sql_info = mydb_cursor.execute("select Instrument_Number, Instrument_ID, Part_ID, Series, Var_Suffix, var_id from vw_Instrument_VarDetails where (Part_ID = ?)",(partid)).fetchone()
        mydb.close()
        
        if partid_sql_info == None:
            self.specInstrumentNumber.clear()
            self.specInstrumentNumber.setPlaceholderText("Spec. Instrument Number")
            self.spec_ntwk = None
            self.Instrument_ID = None
        else:
            self.specInstrumentNumber.setText(f'{partid_sql_info.Instrument_Number} {partid_sql_info.Var_Suffix}')
            self.Instrument_ID = partid_sql_info.Instrument_ID
            self.get_specification_network()

    def get_specification_network(self):
        allowed_spec = ['MWV-001', 'MWV-004', 'MWV-005', 'MWV-052', 'MWV-059']  # Currently supports Frequency Band, VSWR, IL, RL, and Passband Frequency
        spec_list = []
        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        for row in mydb_cursor.execute("select Flann_Ref, Instrument_ID, NumNom, NumLwr, NumUpr from qry_InstrumentParameter_Search where (Flann_Ref like '%MWV%') and (Instrument_ID = ?)",(self.Instrument_ID)):
            if row.Flann_Ref in allowed_spec:
                spec_list.append([row.Flann_Ref,row.NumNom,row.NumLwr,row.NumUpr])
        mydb.close()
        try:
            s11, s21 = 0, 0
            for i in range(len(spec_list)):
                if spec_list[i][0] == 'MWV-052' or spec_list[i][0] == 'MWV-001':
                    freq = skrf.Frequency.from_f([spec_list[i][2], spec_list[i][3]], unit='Hz')
                elif spec_list[i][0] == 'MWV-004':
                    s11 = (abs(float(spec_list[i][1])) - 1) / (abs(float(spec_list[i][1])) + 1)
                elif spec_list[i][0] == 'MWV-059':
                    s11 = 10 ** (- abs(float(spec_list[i][1])) / 20)
                elif spec_list[i][0] == 'MWV-005':
                    s21 = 10 ** (- abs(float(spec_list[i][1])) / 20)
            s_matrix = np.zeros((2, 2, 2), dtype=complex)
            s_matrix[:, 0, 0] = s11
            s_matrix[:, 1, 0] = s21
            s_matrix[:, 0, 1] = s21
            s_matrix[:, 1, 1] = s11
            self.spec_ntwk = skrf.Network(frequency=freq, s=s_matrix, name='Spec')
            self.ntwk_plot.set_networks(self.spec_ntwk)
        except Exception:
            return

    def save_network_item(self, ntwk_list_item=None):
        partid = self.partid.text()
        sn = self.serialNumber.text()
        text = self.notesTextBox.toPlainText()
        operator = self.operatorNumber.value()
        analyser = self.analyserComboBox.currentText()
        date = QtCore.QDateTime.currentDateTime().toString("yyyyMMdd")
        time = QtCore.QDateTime.currentDateTime().toString("hhmm")
        # ntwk = ntwk_list_item.ntwk
        property_dict = {'part_id': partid, 'spec': [[0.1,0.9],[0.1,0.9]], 'operator': operator, 'anlysr': analyser, 'date': date, 'time': time, 'notes': text}
        print(property_dict)
        if isinstance(self.ntwk, skrf.Network):
            self.ntwk.comments = str(property_dict)
            self.ntwk.write_touchstone(f'{sn}_{date}_{time}', skrf_comment=False)

        # if not isinstance(ntwk, skrf.Network):
        #     raise TypeError("ntwk must be a skrf.Network object to save")
        

