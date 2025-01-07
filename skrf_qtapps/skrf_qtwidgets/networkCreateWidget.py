import os
import re
import skrf
import pyodbc
from collections import OrderedDict

from qtpy import QtCore, QtWidgets

from . import widgets
from .networkPlotWidget import NetworkPlotWidget
from .analyzers import analyzers

testDataPath = '\\\\Filesrv\\Test\\RFData\\'
mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
mydb_cursor = mydb.cursor()


class NetworkInstrument(skrf.Network):
    def __init__(self, part_id: str = None, spec: list = None, operator: int = None, anlysr: str = None, notes: str = None, ntwk: skrf.Network = None):
        super().__init__()
        self.part_id = part_id
        self.notes = notes
        self.spec = spec
        self.operator = operator
        self.anlysr = anlysr
        self.ntwk = ntwk

    def update_network(self, info):
        pass


class NetworkCreateWidget(QtWidgets.QWidget):
    item_removed = QtCore.Signal()
    item_updated = QtCore.Signal(object)
    save_single_requested = QtCore.Signal(object, str)
    selection_changed = QtCore.Signal(object)
    same_item_clicked = QtCore.Signal(object)
    state_changed = QtCore.Signal()

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        self.ntwk = None

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
                self.s_paramGroup.addButton(button, id=(j+4*1))
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

    def get_analyzer(self):
        nwa = None
        try:
            nwa = analyzers[self.analyserComboBox.currentText()](self.analyserAddress.text())
        except Exception:
            print('Unable to get analyzer')
        print(nwa)
        return nwa
    
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
        self.ntwk = self.get_analyzer().get_snp_network((1,2))
        if self.serialNumber.text():
            self.ntwk.name = self.serialNumber.text()
        # self.ntwk = skrf.Network('test.s2p')
        
        self.ntwk_plot.set_networks(self.ntwk)

    def get_instument_number(self):
        self.instrumentNumberInfoDict.clear()
        self.partid.setText(self.partid.text().upper())
        partid = self.partid.text()
        partid_sql_info = mydb_cursor.execute("select Instrument_Number, Part_ID, Series, Var_Suffix, var_id from vw_Instrument_VarDetails where (Part_ID = ?)",(partid)).fetchone()
        
        if partid_sql_info == None:
            self.specInstrumentNumber.clear()
            self.specInstrumentNumber.setPlaceholderText("Spec. Instrument Number")
        else:
            self.specInstrumentNumber.setText(f'{partid_sql_info.Instrument_Number} {partid_sql_info.Var_Suffix}')

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
        

