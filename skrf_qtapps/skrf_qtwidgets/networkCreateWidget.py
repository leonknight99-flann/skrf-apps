import os
import sys
import re
import skrf
import numpy as np
import pyodbc
from collections import OrderedDict
import tempfile

import matplotlib.pyplot as plt

from qtpy import QtCore, QtWidgets

from . import widgets, qt
from .networkPlotWidget import NetworkPlotWidget
from .analyzers import loaded_analyzers
from sql_qtwidgets import ismSpecTranslate

testDataPath = '\\\\Filesrv\\Test\\RFData\\'
tempFileDefaultName = 'flannalyser_tempfile'


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
        self.analyser_IFBW = None
        self.analyser_averaging = None
        self.analyser_averaging_count = None
        self.spec_ntwk = None

        self.tempdir = tempfile.gettempdir()

        self.verticalLayout_main = QtWidgets.QVBoxLayout(self)  # Primary Widget Layout
        self.verticalLayout_main.setContentsMargins(0, 0, 0, 0)

        self.analyserLabel = QtWidgets.QLabel("Analyser:") # Row1
        self.analyserComboBox = QtWidgets.QComboBox()
        self.analyserAddressLabel = QtWidgets.QLabel("Address:")
        self.analyserAddress = QtWidgets.QLineEdit()
        self.analyserAddress.setPlaceholderText("VISA String")

        self.analyserComboBox.currentIndexChanged.connect(self.update_selected_analyzer)
        for key in loaded_analyzers.keys():
            self.analyserComboBox.addItem(key)

        self.openButton = QtWidgets.QPushButton("Clear Network")
        self.openButton.released.connect(lambda: self.delete_temp_networks())

        self.captureButton = QtWidgets.QPushButton("Capture Data")
        self.captureButton.clicked.connect(lambda: self.capture_data())

        self.importButton = QtWidgets.QPushButton("Import Captured Data")
        self.importButton.setDisabled(True)

        self.partidLabel = QtWidgets.QLabel("Part ID:") # Row2
        self.partid = QtWidgets.QLineEdit()
        self.partid.setPlaceholderText("Part ID or Test Data Folder Name")
        self.instrumentNumberInfoDict = {}
        self.partid.textChanged.connect(lambda: self.get_instument_number())

        self.specInstrumentNumber = QtWidgets.QLineEdit()
        self.specInstrumentNumber.setPlaceholderText("Spec. Instrument Number")
        self.specInstrumentNumber.setReadOnly(True)

        self.serialNumber = QtWidgets.QLineEdit()
        self.serialNumber.setPlaceholderText("Serial Number")

        self.plus1Button = QtWidgets.QPushButton("+1")
        self.plus1Button.clicked.connect(lambda: self.plus1_serial_number())

        self.failFlagButton = QtWidgets.QPushButton("Fail Flag")
        self.failFlagButton.setCheckable(True)
        self.failFlagButton.setStyleSheet("QPushButton:checked { background-color: red; color: white; }")

        self.numberPortsLabel = QtWidgets.QLabel("Number\nof Ports:")
        self.numberPorts = QtWidgets.QSpinBox()
        self.numberPorts.setMinimum(1)
        self.numberPorts.setMaximum(4)
        self.numberPorts.setValue(2)
        self.numberPorts.valueChanged.connect(lambda: self.update_s_param())

        self.notesTextBox = QtWidgets.QPlainTextEdit()
        self.notesTextBox.setPlaceholderText("Notes")
        
        self.operatorNumberLabel = QtWidgets.QLabel("Operator:") # Row-1
        self.operatorNumber = QtWidgets.QSpinBox()
        self.operatorNumber.setMinimum(1)
        self.operatorNumber.setMaximum(999)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(lambda: self.save_network_item())

        '''COM Connection'''

        self.address = QtWidgets.QLineEdit()
        self.address.setPlaceholderText("COM Port")

        self.connectCOMButton = QtWidgets.QPushButton("Connect")
        self.connectCOMButton.setCheckable(True)
        self.connectCOMButton.setStyleSheet("QPushButton:checked { background-color: lightgreen; }")

        '''024 Controls'''

        self.position024 = QtWidgets.QLineEdit()
        self.position024.setPlaceholderText("Position step/dB")
        self.setPosition024Button = QtWidgets.QPushButton("Goto")

        self.findcoeff024Button = QtWidgets.QPushButton("Find Coeff")

        '''337 Controls'''

        self.pos1Button = QtWidgets.QPushButton("Position 1")
        self.pos1Button.setCheckable(True)
        self.pos1Button.clicked.connect(lambda: self.pos2Button.setChecked(False))
        self.pos1Button.setStyleSheet("QPushButton:checked { background-color: lightblue; }")
        self.pos2Button = QtWidgets.QPushButton("Position 2")
        self.pos2Button.setCheckable(True)
        self.pos2Button.clicked.connect(lambda: self.pos1Button.setChecked(False))
        self.pos2Button.setStyleSheet("QPushButton:checked { background-color: lightblue; }")

        self.switchPortGroup = QtWidgets.QButtonGroup()
        self.switchPortGroup.setExclusive(False)
        self.switch41Button = QtWidgets.QRadioButton('Port 4-1')
        self.switchPortGroup.addButton(self.switch41Button)
        self.switch12Button = QtWidgets.QRadioButton('Port 1-2')
        self.switchPortGroup.addButton(self.switch12Button)
        self.switch23Button = QtWidgets.QRadioButton('Port 2-3')
        self.switchPortGroup.addButton(self.switch23Button)
        self.switch34Button = QtWidgets.QRadioButton('Port 3-4')
        self.switchPortGroup.addButton(self.switch34Button)

        '''S-Parameter Buttons'''

        self.s_paramButtons = {}

        self.s_paramLayout = QtWidgets.QGridLayout()
        self.s_paramGroup = QtWidgets.QButtonGroup()
        
        for i in range(4):
            for j in range(4):
                button = QtWidgets.QRadioButton(f'S{i+1}{j+1}')
                self.s_paramLayout.addWidget(button, i, j)
                self.s_paramGroup.addButton(button, id=(j+4*i))  # Button ids are 0-15 for S11,S12,S13,...,S44
        self.s_paramGroup.setExclusive(False)
        self.update_s_param()

        '''Layout Setup'''

        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()

        self.instrumentTabWidget = QtWidgets.QTabWidget(self)
        # self.instrumentTabWidget.setCornerWidget(self.serialNumber, QtCore.Qt.TopRightCorner)
        self.instrumentTabWidget.addTab(self.tab1, "Home")
        self.instrumentTabWidget.addTab(self.tab2, "COM")
        self.instrumentTabWidget.addTab(self.tab3, "024")
        self.instrumentTabWidget.addTab(self.tab4, "337")

        self.row1 = QtWidgets.QHBoxLayout() # Row1
        self.row1.addWidget(self.analyserLabel)
        self.row1.addWidget(self.analyserComboBox)
        self.row1.addWidget(self.analyserAddressLabel)
        self.row1.addWidget(self.analyserAddress)

        self.row2 = QtWidgets.QHBoxLayout() # Row2
        self.row2.addWidget(self.partidLabel)
        self.row2.addWidget(self.partid)

        self.row3 = QtWidgets.QHBoxLayout() # Row3
        self.row3.addWidget(self.instrumentTabWidget)

        self.tab1.layout = QtWidgets.QHBoxLayout()
        self.tab1.layout.addWidget(self.failFlagButton)
        self.tab1.layout.addWidget(self.plus1Button)
        self.tab1.layout.addWidget(self.numberPortsLabel)
        self.tab1.layout.addWidget(self.numberPorts)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QtWidgets.QHBoxLayout()
        self.tab2.layout.addWidget(self.address)
        self.tab2.layout.addWidget(self.connectCOMButton)
        self.tab2.setLayout(self.tab2.layout)

        self.tab3.layout = QtWidgets.QHBoxLayout()
        self.tab3.layout.addWidget(self.findcoeff024Button)
        self.tab3.layout.addWidget(self.position024)
        self.tab3.layout.addWidget(self.setPosition024Button)
        self.tab3.setLayout(self.tab3.layout)

        self.tab4.layout = QtWidgets.QVBoxLayout()
        self.tab4row1 = QtWidgets.QHBoxLayout()
        self.tab4row1.addWidget(self.switch41Button)
        self.tab4row1.addWidget(self.switch12Button)
        self.tab4row1.addWidget(self.switch23Button)
        self.tab4row1.addWidget(self.switch34Button)
        self.tab4row2 = QtWidgets.QHBoxLayout()
        self.tab4row2.addWidget(self.pos1Button)
        self.tab4row2.addWidget(self.pos2Button)
        self.tab4.layout.addLayout(self.tab4row1)
        self.tab4.layout.addLayout(self.tab4row2)
        self.tab4.setLayout(self.tab4.layout)

        self.rowFinal = QtWidgets.QHBoxLayout() # Row-1
        self.rowFinal.addWidget(self.operatorNumberLabel)
        self.rowFinal.addWidget(self.operatorNumber)
        self.rowFinal.addWidget(self.openButton)
        self.rowFinal.addWidget(self.saveButton)

        self.verticalLayout_main.addLayout(self.row1)
        self.verticalLayout_main.addLayout(self.row2)
        self.verticalLayout_main.addWidget(self.specInstrumentNumber)
        self.verticalLayout_main.addWidget(self.serialNumber)
        self.verticalLayout_main.addLayout(self.row3)
        self.verticalLayout_main.addWidget(self.captureButton)
        self.verticalLayout_main.addLayout(self.s_paramLayout)
        self.verticalLayout_main.addWidget(self.importButton)
        self.verticalLayout_main.addWidget(self.notesTextBox)

        self.verticalLayout_main.addLayout(self.rowFinal)  

    def update_selected_analyzer(self):
        cls = loaded_analyzers[self.analyserComboBox.currentText()]
        self.analyserAddress.setText(cls.DEFAULT_VISA_ADDRESS)

    def get_analyzer_network(self, ports):
        nwa = None
        try:
            nwa = loaded_analyzers[self.analyserComboBox.currentText()](self.analyserAddress.text(), backend='C:\\WINDOWS\\system32\\visa32.dll')  # Change backend to 'py' for pyvisa-py using NI-VISA
        except Exception:
            print('Unable to get analyzer')
            return
        
        self.analyser_IFBW = nwa.if_bandwidth
        # self.analyser_averaging = nwa.averaging_on()
        # if self.analyser_averaging:
        #     self.analyser_averaging_count = nwa.averaging_count()
        # else:
        #     self.analyser_averaging_count = None
        
        ntwk = nwa.get_snp_network(ports)  # Get the network from the analyzer

        if hasattr(nwa, 'close'):
            nwa.close()
        else:
            nwa._resource.close()
        return ntwk

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
    
    def update_s_param(self):
        num_ports = self.numberPorts.value()
        for i in range(4):
            for j in range(4):
                button = self.s_paramGroup.button(j + 4 * i)
                if i < num_ports and j < num_ports:
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)
                    button.setChecked(False)

    def capture_data(self):
        if not self.ntwk_plot:
            return
        ntwk_list = []
        ntwk = None
        checked_buttons = [i for i, button in enumerate(self.s_paramGroup.buttons()) if button.isChecked()] # Checked buttons are 0-15, i%4 is the column, i//4 is the row
        
        try:
            if checked_buttons == [0]:
                ntwk = self.get_analyzer_network((1,))
            elif checked_buttons == [5]:
                ntwk = self.get_analyzer_network((2,))
            else:
                ntwk = self.get_analyzer_network((1,2))
            if self.serialNumber.text():
                ntwk.name = self.serialNumber.text()
            
            if isinstance(ntwk, skrf.Network):
                ntwk_list.append(ntwk)

            if isinstance(self.spec_ntwk, skrf.Network):
                ntwk_list.append(self.spec_ntwk)

            if ntwk_list:
                ntwk_with_spec = ntwk_list if len(ntwk_list) > 1 else ntwk_list[0]
            
            self.ntwk_plot.set_networks(ntwk_with_spec)

            ntwk.write_touchstone(os.path.join(self.tempdir, f'{tempFileDefaultName}_{self.serialNumber.text()}_p12'), skrf_comment=False)

        except Exception:
            qt.error_popup('Analyzer not found\n\nPlease check the VISA address and try again')

    def delete_temp_networks(self):
        if self.ntwk_plot:
            self.ntwk_plot.clear_plot()
        tempdir = self.tempdir
        for file in os.listdir(tempdir):
            if file.startswith(tempFileDefaultName):
                try:
                    os.remove(os.path.join(tempdir, file))
                except Exception as e:
                    qt.error_popup(f'Error removing temp file {file}: {e}')

    def get_instument_number(self):  # Trys to get the Instrument Number from the user entered Part ID
        if self.ntwk_plot:
            self.ntwk_plot.clear_plot()
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
            self.spec_ntwk = ismSpecTranslate.get_specification_network([self.Instrument_ID])
            self.ntwk_plot.set_networks(self.spec_ntwk)

    def plus1_serial_number(self):
        current_text = self.serialNumber.text()
        if not current_text:
            return
        elif current_text[-1].isdigit():
            new_text = re.sub(r'(\d+)$', lambda x: str(int(x.group(0)) + 1).zfill(len(x.group(0))), current_text)
        else:
            new_text = current_text + '1'
        self.serialNumber.setText(new_text)

    def save_network_item(self):

        # try:
        tempFileList = [f for f in os.listdir(self.tempdir) if f.startswith(tempFileDefaultName)]
        print(tempFileList)
        ntwk = skrf.Network(os.path.join(self.tempdir,tempFileList[0]))  # Load the captured network from the temp file, eventually this will need a combined network
        # except Exception:
        #     qt.error_popup('Save failed - no network to save')

        partid = self.partid.text()
        sn = self.serialNumber.text()
        text = self.notesTextBox.toPlainText()
        operator = self.operatorNumber.value()
        analyser = self.analyserComboBox.currentText()
        analyser_IFBW = self.analyser_IFBW
        analyser_averaging = self.analyser_averaging
        analyser_averaging_count = self.analyser_averaging_count
        date = QtCore.QDateTime.currentDateTime().toString("yyyyMMdd")
        time = QtCore.QDateTime.currentDateTime().toString("hhmm")

        spec_dict = {}

        spec_dict_filter = ['MWV', 'MEC-001', 'MEC-002', 'MEC-004', 'MEC-005', 'MEC-035', 'MEC-040', 'MEC-016']

        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        for row in mydb_cursor.execute("select Flann_Ref, Instrument_ID, Units, Nominal, TolType, UprTol, LwrTol, ApprovedDate from qry_InstrumentParameter_Search where (Instrument_ID = ?)",(self.Instrument_ID)):
            spec_dict[row.Flann_Ref] = ([row.Nominal,row.Units,row.TolType,row.UprTol,row.LwrTol,row.ApprovedDate])
        mydb.close()

        spec_dict = {k:v for k,v in spec_dict.items() if any(s in k for s in spec_dict_filter)}

        property_dict = {'part_id': partid, 'spec': spec_dict, 'fail': False, 'operator': operator, 
                         'analyser': analyser, 'analyser_IFBW': analyser_IFBW, 'analyser_averaging': analyser_averaging, 
                         'analyser_averaging_count': analyser_averaging_count, 'date': date, 'time': time, 'notes': text}

        if not os.path.exists(testDataPath + partid):
            print(f'Creating directory: {testDataPath + partid}')
            os.makedirs(testDataPath + partid)

        if self.failFlagButton.isChecked():
            property_dict['fail'] = True
            sn = f'{sn}_FAIL'

        if isinstance(ntwk, skrf.Network):
            ntwk.comments = str(property_dict)
            ntwk.write_touchstone(f'{testDataPath + partid}\\{sn}_{date}_{time}', skrf_comment=False)
            qt.MessageBox('Save Successful', title='Save').exec_()
            self.delete_temp_networks()

        if not isinstance(ntwk, skrf.Network):
            qt.error_popup('Save failed - no network to save')
        

