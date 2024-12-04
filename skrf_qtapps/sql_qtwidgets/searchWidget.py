import os
import pyodbc

from qtpy import QtWidgets

file_types = ('.csv', '.s1p', '.s2p', '.s3p', '.s4p')
testDataPath = '\\\\Filesrv\\Test\\RFData\\'
mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
mydb_cursor = mydb.cursor()


class SQLDataSearchWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        ## --- Setup UI Elements --- ~
        self.verticalLayout = QtWidgets.QVBoxLayout(self) # primary widget layout
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.label_instNum = QtWidgets.QLabel("Input Instrument Number", self)
        self.lineEdit_instNum = QtWidgets.QLineEdit(self)
        self.label_partID = QtWidgets.QLabel("Input Part ID", self)
        self.lineEdit_partID = QtWidgets.QLineEdit(self)
        self.label_filter = QtWidgets.QLabel("Filter File List", self)
        self.lineEdit_filter = QtWidgets.QLineEdit(self)
        self.plot_button = QtWidgets.QPushButton("Plot")
        self.hlayout_getScan = QtWidgets.QHBoxLayout()
        self.hlayout_getScan.addWidget(self.label_instNum)
        self.hlayout_getScan.addWidget(self.lineEdit_instNum)
        self.hlayout_getScan.addWidget(self.label_partID)
        self.hlayout_getScan.addWidget(self.lineEdit_partID)
        self.hlayout_getScan.addWidget(self.label_filter)
        self.hlayout_getScan.addWidget(self.lineEdit_filter)
        self.hlayout_getScan.addWidget(self.plot_button)

        self.hlayout_lists = QtWidgets.QHBoxLayout()

        self.listWidget_PartIDs = QtWidgets.QListWidget(self)
        self.listWidget_PartIDs.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.scrollBar_PartIDs = QtWidgets.QScrollBar(self)
        self.listWidget_PartIDs.setVerticalScrollBar(self.scrollBar_PartIDs)

        self.listWidget_SerialNums = QtWidgets.QListWidget(self)
        self.listWidget_SerialNums.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.scrollBar_SerialNums = QtWidgets.QScrollBar(self)
        self.listWidget_SerialNums.setVerticalScrollBar(self.scrollBar_SerialNums)

        self.hlayout_lists.addWidget(self.listWidget_PartIDs)
        self.hlayout_lists.addWidget(self.listWidget_SerialNums)

        self.verticalLayout.addLayout(self.hlayout_getScan)
        self.verticalLayout.addLayout(self.hlayout_lists)

        # --- End Setup UI Elements --- #

        self.lineEdit_instNum.textChanged.connect(self.list_partids)
        self.lineEdit_partID.textChanged.connect(self.list_partids)
        self.lineEdit_filter.textChanged.connect(self.list_data_files)
        self.listWidget_PartIDs.itemSelectionChanged.connect(self.list_data_files)
        self.listWidget_SerialNums.itemSelectionChanged.connect(self.get_file_list)

        self.partIDsList, self.serialNumsFilesList, self.selected_sns = [], [], []
        

    def list_partids(self):
        self.listWidget_PartIDs.clear()
        self.partIDsList.clear()
        display_pIDs = []
        
        InstNum = self.lineEdit_instNum.text()
        PartID = self.lineEdit_partID.text()
        for row in mydb_cursor.execute("select Instrument_Number, Part_ID, Series, Var_Suffix from vw_Instrument_VarDetails where ((Instrument_Number like ?) and (Part_ID is not null)) and (Part_ID like ?)", ('%'+InstNum+'%', '%'+PartID+'%')):
            display_pIDs.append(f'{row.Instrument_Number} {row.Var_Suffix} {row.Part_ID}')
            self.partIDsList.append(row.Part_ID)
        self.listWidget_PartIDs.addItems(display_pIDs)
    
    def list_data_files(self):
        self.listWidget_SerialNums.clear()
        display_sn = []
        self.serialNumsFilesList.clear()

        selected_pIDs = [p.row() for p in self.listWidget_PartIDs.selectedIndexes()]
        selected_pIDs = [self.partIDsList[p] for p in selected_pIDs]

        for dir in selected_pIDs:
            try:
                list_files = os.listdir(testDataPath+dir)
                list_files = [name for name in list_files if name.lower().endswith(file_types)]
                if self.lineEdit_filter.text() != '':
                    filter_list = self.lineEdit_filter.text().split(',')
                    list_files = list(filter(lambda f: any(s in f.lower() for s in filter_list), list_files))
                self.serialNumsFilesList += [testDataPath+dir+'\\'+s for s in list_files]
                display_sn += list_files
            except:
                continue
        self.listWidget_SerialNums.addItems(display_sn)

    def get_selected_files(self):
        selected_sns = [s.text() for s in self.listWidget_SerialNums.selectedItems()]
        return selected_sns
    
    def get_file_list(self):
        serialNumsFilesList = self.serialNumsFilesList
        return serialNumsFilesList
