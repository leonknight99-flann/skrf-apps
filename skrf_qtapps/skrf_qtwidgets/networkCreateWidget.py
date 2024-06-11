import os
import re
import skrf
from collections import OrderedDict

from qtpy import QtCore, QtWidgets

from skrf_qtwidgets import widgets


class CreateNetworkWidget(QtWidgets.QWidget):
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

        self.newNetworkLabel = QtWidgets.QLabel("Number of Ports:") # Row1
        self.newNetworkSpinBox = QtWidgets.QSpinBox()
        self.newNetworkSpinBox.setMinimum(1)
        self.newNetworkSpinBox.setMaximum(4)
        self.createNewNetworkButton = QtWidgets.QPushButton("Create")

        self.openButton = QtWidgets.QPushButton("Open Network")
        self.openButton.released.connect(self.load_from_files)

        self.captureButton = QtWidgets.QPushButton("Capture Data")

        self.partidLabel = QtWidgets.QLabel("Part ID:") # Row2
        self.partid = QtWidgets.QLineEdit()

        self.serialNumber = QtWidgets.QLineEdit()
        self.serialNumber.setPlaceholderText("Serial Number")

        self.notesTextBox = QtWidgets.QPlainTextEdit()
        self.notesTextBox.setPlaceholderText("Notes")
        
        self.operatorNumberLabel = QtWidgets.QLabel("Operator:") # Row-1
        self.operatorNumber = QtWidgets.QSpinBox()
        self.operatorNumber.setMinimum(1)
        self.operatorNumber.setMaximum(100)
        self.saveButton = QtWidgets.QPushButton("Save")

        self.s_paramButtons = {}

        self.s_paramLayout = QtWidgets.QGridLayout()
        self.s_paramGroup = QtWidgets.QButtonGroup()
        
        for i in range(4):
            for j in range(4):
                button = QtWidgets.QRadioButton(f'S{i+1}{j+1}')
                self.s_paramLayout.addWidget(button, i, j)
                self.s_paramGroup.addButton(button, id=(j+4*1))
        self.s_paramGroup.setExclusive(False)

        self.row1 = QtWidgets.QHBoxLayout() # Row1
        self.row1.addWidget(self.newNetworkLabel)
        self.row1.addWidget(self.newNetworkSpinBox)
        self.row1.addWidget(self.createNewNetworkButton)

        self.row2 = QtWidgets.QHBoxLayout() # Row2
        self.row2.addWidget(self.partidLabel)
        self.row2.addWidget(self.partid)

        self.rowFinal = QtWidgets.QHBoxLayout() # Row-1
        self.rowFinal.addWidget(self.operatorNumberLabel)
        self.rowFinal.addWidget(self.operatorNumber)
        self.rowFinal.addWidget(self.saveButton)

        # self.verticalLayout_main.addLayout(self.row1)
        self.verticalLayout_main.addWidget(self.openButton)
        self.verticalLayout_main.addLayout(self.s_paramLayout)
        self.verticalLayout_main.addWidget(self.captureButton)
        self.verticalLayout_main.addLayout(self.row2)
        self.verticalLayout_main.addWidget(self.serialNumber)
        self.verticalLayout_main.addWidget(self.notesTextBox)

        self.verticalLayout_main.addLayout(self.rowFinal)   
    
    def load_networks(self, ntwks):
        if not ntwks:
            return
        
    def load_from_files(self, caption="load touchstone file"):
        self.load_networks(widgets.load_network_files(caption))
        

