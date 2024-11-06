import os
import re
import skrf
from collections import OrderedDict

from qtpy import QtCore, QtWidgets

from . import widgets
from .networkPlotWidget import NetworkPlotWidget

class NetworkCreateItem(skrf.Network):
    def __init__(self, part_id: str = None, name: str = None, spec: list = None,
                 operator: int = None, anlysr: str = None, notes: str = None,
                 ntwk: skrf.Network = None):
        self.part_id = part_id
        self.name = name
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

        self.verticalLayout_main = QtWidgets.QVBoxLayout(self)  # Primary Widget Layout
        self.verticalLayout_main.setContentsMargins(0, 0, 0, 0)

        self.analyserLabel = QtWidgets.QLabel("Analyser:") # Row1
        self.analyserComboBox = QtWidgets.QComboBox()
        self.analyserAddressLabel = QtWidgets.QLabel("Address:")
        self.analyserAddress = QtWidgets.QLineEdit()
        self.analyserAddress.setPlaceholderText("VISA String")

        self.openButton = QtWidgets.QPushButton("Open Network")
        self.openButton.released.connect(self.load_from_files)
        self.openButton.setDisabled(True)  # Remove once the feature has been added

        self.captureButton = QtWidgets.QPushButton("Capture Data")
        self.captureButton.clicked.connect(lambda: self.capture_data())

        self.importButton = QtWidgets.QPushButton("Import Captured Data")
        self.importButton.setDisabled(True)

        self.partidLabel = QtWidgets.QLabel("Part ID:") # Row2
        self.partid = QtWidgets.QLineEdit()

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
        
        ntwk = skrf.Network('test.s2p')
        self.ntwk_plot.set_networks(ntwk)

    def save_network_item(self, ntwk_list_item=None):
        partid = self.partid.text()
        sn = self.serialNumber.text()
        text = self.notesTextBox
        print(partid)
        print(sn)
        # ntwk = ntwk_list_item.ntwk

        # if not isinstance(ntwk, skrf.Network):
        #     raise TypeError("ntwk must be a skrf.Network object to save")
        

