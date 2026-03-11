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
from qtpy.QtWidgets import QSizePolicy

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

        self.clearNetworkButton = QtWidgets.QPushButton("Clear Network")
        self.clearNetworkButton.released.connect(lambda: self.delete_temp_networks())

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

        self.plus1Button = QtWidgets.QPushButton("S/N +1")
        self.plus1Button.clicked.connect(lambda: self.plus1_serial_number())

        self.failFlagButton = QtWidgets.QPushButton("Fail Flag")
        self.failFlagButton.setCheckable(True)
        self.failFlagButton.setStyleSheet("QPushButton:checked { background-color: red; color: white; }")

        self.numberPortsLabel = QtWidgets.QLabel("Number of Ports:")
        self.numberPorts = QtWidgets.QSpinBox()
        self.numberPorts.setMinimum(1)
        self.numberPorts.setMaximum(4)
        self.numberPorts.setValue(2)
        self.numberPorts.valueChanged.connect(lambda: self.update_port_combo())

        self.slidingLoadButton = QtWidgets.QPushButton("Sliding Load")
        self.slidingLoadButton.setCheckable(True)
        self.slidingLoadButton.setStyleSheet("QPushButton:checked { background-color: green; color: white; }")
        self.slidingLoadButton.toggled.connect(lambda: self.slidingLoadPosition.setEnabled(self.slidingLoadButton.isChecked()))

        self.slidingLoadLabel = QtWidgets.QLabel("Position (1-8):")
        self.slidingLoadPosition = QtWidgets.QSpinBox()
        self.slidingLoadPosition.setMinimum(1)
        self.slidingLoadPosition.setMaximum(8)
        self.slidingLoadPosition.setValue(1)
        self.slidingLoadPosition.setEnabled(False)

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

        '''S-Parameter Selection'''

        self.portRow = QtWidgets.QHBoxLayout()

        self.port_list = ['OFF', '1', '2', '3', '4']
        self.port1_s_paramComboBox = QtWidgets.QComboBox()
        self.port1_s_paramComboBox.addItems(self.port_list[:self.numberPorts.value()+1])
        self.port1_s_paramComboBox.setCurrentIndex(1)
        self.port2_s_paramComboBox = QtWidgets.QComboBox()
        self.port2_s_paramComboBox.addItems(self.port_list[:self.numberPorts.value()+1])
        self.port2_s_paramComboBox.setCurrentIndex(2)

        self.portRow.addWidget(QtWidgets.QLabel("Port 1 S-Param:"))
        self.portRow.addWidget(self.port1_s_paramComboBox)
        self.portRow.addWidget(QtWidgets.QLabel("Port 2 S-Param:"))
        self.portRow.addWidget(self.port2_s_paramComboBox)

        '''Layout Setup'''

        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()

        self.instrumentTabWidget = QtWidgets.QTabWidget(self)
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

        self.tab1.layout = QtWidgets.QVBoxLayout()
        self.tab1row1 = QtWidgets.QHBoxLayout()
        self.tab1row1.addWidget(self.failFlagButton)
        self.tab1row1.addWidget(self.plus1Button)
        self.tab1row2 = QtWidgets.QHBoxLayout()
        self.tab1row2.addWidget(self.numberPortsLabel)
        self.tab1row2.addWidget(self.numberPorts)
        self.tab1row3 = QtWidgets.QHBoxLayout()
        self.tab1row3.addWidget(self.slidingLoadButton)
        self.tab1row3.addWidget(self.slidingLoadLabel)
        self.tab1row3.addWidget(self.slidingLoadPosition)
        self.tab1.layout.addLayout(self.tab1row1)
        self.tab1.layout.addLayout(self.tab1row2)
        self.tab1.layout.addLayout(self.tab1row3)
        self.tab1.layout.addStretch()
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QtWidgets.QVBoxLayout()
        self.tab2row1 = QtWidgets.QHBoxLayout()
        self.tab2row1.addWidget(self.address)
        self.tab2row1.addWidget(self.connectCOMButton)
        self.tab2.layout.addLayout(self.tab2row1)
        self.tab2.layout.addStretch()
        self.tab2.setLayout(self.tab2.layout)

        self.tab3.layout = QtWidgets.QVBoxLayout()
        self.tab3row1 = QtWidgets.QHBoxLayout()
        self.tab3row1.addWidget(self.findcoeff024Button)
        self.tab3row1.addWidget(self.position024)
        self.tab3row1.addWidget(self.setPosition024Button)
        self.tab3.layout.addLayout(self.tab3row1)
        self.tab3.layout.addStretch()
        self.tab3.setLayout(self.tab3.layout)

        self.tab4.layout = QtWidgets.QVBoxLayout()
        self.tab4row1 = QtWidgets.QHBoxLayout()
        self.tab4row1.addWidget(self.pos1Button)
        self.tab4row1.addWidget(self.pos2Button)
        self.tab4.layout.addLayout(self.tab4row1)
        self.tab4.layout.addStretch()
        self.tab4.setLayout(self.tab4.layout)

        self.rowFinal = QtWidgets.QHBoxLayout() # Row-1
        self.rowFinal.addWidget(self.operatorNumberLabel)
        self.rowFinal.addWidget(self.operatorNumber)
        self.rowFinal.addWidget(self.clearNetworkButton)
        self.rowFinal.addWidget(self.saveButton)

        self.verticalLayout_main.addLayout(self.row1)
        self.verticalLayout_main.addLayout(self.row2)
        self.verticalLayout_main.addWidget(self.specInstrumentNumber)
        self.verticalLayout_main.addWidget(self.serialNumber)
        self.verticalLayout_main.addLayout(self.row3)
        self.verticalLayout_main.addLayout(self.portRow)
        self.verticalLayout_main.addWidget(self.captureButton)
        self.verticalLayout_main.addWidget(self.importButton)
        self.verticalLayout_main.addWidget(self.notesTextBox)

        self.verticalLayout_main.addLayout(self.rowFinal)  

    def update_port_combo(self):
        port1_currentIdex = self.port1_s_paramComboBox.currentIndex()
        port2_currentIdex = self.port2_s_paramComboBox.currentIndex()

        if port1_currentIdex > self.numberPorts.value():
            port1_currentIdex = 0
        if port2_currentIdex > self.numberPorts.value():
            port2_currentIdex = 0

        self.port1_s_paramComboBox.clear()
        self.port1_s_paramComboBox.addItems(self.port_list[:self.numberPorts.value()+1])
        self.port1_s_paramComboBox.setCurrentIndex(port1_currentIdex)

        self.port2_s_paramComboBox.clear()
        self.port2_s_paramComboBox.addItems(self.port_list[:self.numberPorts.value()+1])
        self.port2_s_paramComboBox.setCurrentIndex(port2_currentIdex)

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

    def capture_data(self):
        if not self.ntwk_plot:
            return
        ntwk_list = []
        ntwk = None
        
        try:
            if self.port2_s_paramComboBox.currentIndex() == 0:
                ntwk = self.get_analyzer_network((1,))
                port_number = self.port1_s_paramComboBox.currentText()*2
            elif self.port1_s_paramComboBox.currentIndex() == 0:
                ntwk = self.get_analyzer_network((2,))
                port_number = self.port2_s_paramComboBox.currentText()*2
            else:  # Both ports enabled
                ntwk = self.get_analyzer_network((1,2))
                port_number = self.port1_s_paramComboBox.currentText() + self.port2_s_paramComboBox.currentText()
            if self.serialNumber.text():
                ntwk.name = self.serialNumber.text()
            
            if isinstance(ntwk, skrf.Network):
                ntwk_list.append(ntwk)

            if isinstance(self.spec_ntwk, skrf.Network):
                ntwk_list.append(self.spec_ntwk)

            if ntwk_list:
                ntwk_with_spec = ntwk_list if len(ntwk_list) > 1 else ntwk_list[0]
            
            self.ntwk_plot.set_networks(ntwk_with_spec)

            ntwk.write_touchstone(os.path.join(self.tempdir, f'{tempFileDefaultName}_{self.serialNumber.text()}_P{port_number}'), skrf_comment=False)

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
        print(f'Number of Ports: {self.numberPorts.value()}')
        print(tempFileList)
        
        if self.numberPorts.value() <= 2:
            ntwk = skrf.Network(os.path.join(self.tempdir,tempFileList[0]))  # Load the captured network from the temp file, eventually this will need a combined network

        else:
            ntwk = skrf.n_twoports_2_nport([skrf.Network(os.path.join(self.tempdir,f)) for f in tempFileList], nports=self.numberPorts.value())  # Combine 2-port networks into n-port network
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
        

