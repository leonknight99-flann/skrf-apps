import os
import re
import pyodbc

from qtpy import QtWidgets

file_types = ('.csv', '.s1p', '.s2p', '.s3p', '.s4p')
testDataPath = '\\\\Filesrv\\Test\\RFData\\'


class SQLDataSearchWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        ## --- Setup UI Elements --- ~
        self.verticalLayout = QtWidgets.QVBoxLayout(self) # primary widget layout
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.plotspec_button = QtWidgets.QPushButton("Plot Spec")
        self.lineEdit_instNum = QtWidgets.QLineEdit(self)
        self.lineEdit_partID = QtWidgets.QLineEdit(self)
        self.lineEdit_filter = QtWidgets.QLineEdit(self)
        self.plot_button = QtWidgets.QPushButton("Plot")
        self.hlayout_getScan = QtWidgets.QHBoxLayout()
        self.hlayout_getScan.addWidget(self.plotspec_button)
        self.hlayout_getScan.addWidget(QtWidgets.QLabel("Input Instrument Number"))
        self.hlayout_getScan.addWidget(self.lineEdit_instNum)
        self.hlayout_getScan.addWidget(QtWidgets.QLabel("Input Part ID"))
        self.hlayout_getScan.addWidget(self.lineEdit_partID)
        self.hlayout_getScan.addWidget(QtWidgets.QLabel("Filter File List"))
        self.hlayout_getScan.addWidget(self.lineEdit_filter)
        self.hlayout_getScan.addWidget(self.plot_button)

        self.hlayout_lists = QtWidgets.QHBoxLayout()

        self.listWidget_partIDs = QtWidgets.QListWidget(self)
        self.listWidget_partIDs.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.scrollBar_partIDs = QtWidgets.QScrollBar(self)
        self.listWidget_partIDs.setVerticalScrollBar(self.scrollBar_partIDs)

        self.listWidget_serialNums = QtWidgets.QListWidget(self)
        self.listWidget_serialNums.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.scrollBar_serialNums = QtWidgets.QScrollBar(self)
        self.listWidget_serialNums.setVerticalScrollBar(self.scrollBar_serialNums)

        self.listWidget_dataFiles = QtWidgets.QListWidget(self)
        self.listWidget_dataFiles.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.scrollBar_dataFiles = QtWidgets.QScrollBar(self)
        self.listWidget_dataFiles.setVerticalScrollBar(self.scrollBar_dataFiles)

        self.hlayout_lists.addWidget(self.listWidget_partIDs)
        self.hlayout_lists.addWidget(self.listWidget_serialNums)
        self.hlayout_lists.addWidget(self.listWidget_dataFiles)

        self.verticalLayout.addLayout(self.hlayout_getScan)
        self.verticalLayout.addLayout(self.hlayout_lists)

        # --- End Setup UI Elements --- #

        self.lineEdit_instNum.textChanged.connect(self.list_partids)
        self.lineEdit_partID.textChanged.connect(self.list_partids)
        self.lineEdit_filter.textChanged.connect(self.list_data_files)
        self.listWidget_partIDs.itemSelectionChanged.connect(self.list_serial_numbers)
        self.listWidget_partIDs.itemSelectionChanged.connect(self.list_data_files)
        self.listWidget_partIDs.itemDoubleClicked.connect(self.open_partID_folder)
        self.listWidget_serialNums.itemSelectionChanged.connect(self.list_data_files)
        self.listWidget_dataFiles.itemSelectionChanged.connect(self.get_file_list)

        self.partIDsList, self.serialNoList, self.filesList, self.selected_files = [], [], [], []
        self.instrumentIDdict = {}

    def open_partID_folder(self):
        selected_pIDs = [p.row() for p in self.listWidget_partIDs.selectedIndexes()]
        selected_pIDs = [self.partIDsList[p] for p in selected_pIDs]
        os.startfile(testDataPath+selected_pIDs[0])
        
    def list_partids(self):
        self.listWidget_partIDs.clear()
        self.partIDsList.clear()
        self.instrumentIDdict.clear()
        display_pIDs = []
        
        InstNum = self.lineEdit_instNum.text()
        PartID = self.lineEdit_partID.text()
        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=ISM;UID=FLUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()
        for row in mydb_cursor.execute("select Instrument_Number, Instrument_ID, Part_ID, Series, Var_Suffix from vw_Instrument_VarDetails where ((Instrument_Number like ?) and (Part_ID is not null)) and (Part_ID like ?)", ('%'+InstNum+'%', '%'+PartID+'%')):
            display_pIDs.append(f'{row.Instrument_Number} {row.Var_Suffix} {row.Part_ID}')
            self.partIDsList.append(row.Part_ID)
            if row.Instrument_ID not in self.instrumentIDdict:
                self.instrumentIDdict[row.Instrument_ID] = [row.Part_ID]
            else:
                self.instrumentIDdict[row.Instrument_ID].append(row.Part_ID)
        self.listWidget_partIDs.addItems(display_pIDs)
        mydb.close()

    def list_serial_numbers(self):
        self.listWidget_serialNums.clear()
        display_sns = []

        selected_pIDs = [p.row() for p in self.listWidget_partIDs.selectedIndexes()]
        selected_pIDs = [self.partIDsList[p] for p in selected_pIDs]

        mydb = pyodbc.connect("DRIVER={SQL Server};SERVER=SQLSRV22;DATABASE=SVFLANN;UID=SVUser;PWD=MelonBall", readonly=True)
        mydb_cursor = mydb.cursor()

        for pID in selected_pIDs:
            for row in mydb_cursor.execute(f"select * from [vwSerialHistLookup] where PartId like ?", '%'+pID+'%'):
                display_sns.append(row.Serial)
            for row in mydb_cursor.execute(f"select * from [Serial Master] where PRTNUM_71 like ?", '%'+pID+'%'):
                display_sns.append(row.SERIAL_71)

        mydb.close()
        display_sns = list(dict.fromkeys(display_sns))  # Remove duplicates
        def natural_sort_key(s):
        # Split the string into parts: digits and non-digits
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        display_sns.sort(key=natural_sort_key)
        self.listWidget_serialNums.addItems(display_sns)
    
    def list_data_files(self):
        self.listWidget_dataFiles.clear()
        display_sn = []
        self.filesList.clear()

        selected_sn = [s.text() for s in self.listWidget_serialNums.selectedItems()]
        selected_pIDs = [p.row() for p in self.listWidget_partIDs.selectedIndexes()]
        selected_pIDs = [self.partIDsList[p] for p in selected_pIDs]

        for dir in selected_pIDs:
            try:
                list_files = os.listdir(testDataPath+dir)
                list_files = [name for name in list_files if name.lower().endswith(file_types)]
                if len(selected_sn) > 0:
                    list_files = [name for name in list_files if any(all([s in name.lower(), not name.removeprefix(s)[0].isdigit()]) for s in selected_sn)]  # Filter by serial number
                if self.lineEdit_filter.text() != '':  # Filter by string
                    filter_list = self.lineEdit_filter.text().split(',')
                    disguard_list = [s for s in filter_list if s.startswith('!')]
                    filter_list = list(set(filter_list) - set(disguard_list))
                    disguard_list = [s[1:] for s in disguard_list]
                    if len(filter_list) > 0:
                        list_files = list(filter(lambda f: any(s in f.lower() for s in filter_list), list_files))
                    if len(disguard_list) > 0:
                        list_files = [f for f in list_files if not any(s in f.lower() for s in disguard_list)]
                self.filesList += [testDataPath+dir+'\\'+s for s in list_files]
                display_sn += list_files
            except:
                continue
        self.listWidget_dataFiles.addItems(display_sn)

    def get_selected_files(self):
        selected_files = [s.text() for s in self.listWidget_dataFiles.selectedItems()]
        return selected_files
    
    def get_file_list(self):
        serialNumsFilesList = self.filesList
        return serialNumsFilesList
    
    def get_selected_instrumentIDs(self):
        selected_pIDs = [p.row() for p in self.listWidget_partIDs.selectedIndexes()]
        selected_pIDs = [self.partIDsList[p] for p in selected_pIDs]
        selected_instrumentIDs = []
        for p in selected_pIDs:
            for k, v in self.instrumentIDdict.items():
                if p in v:  # Note - If a specification fails to plot in the future it maybe due to part IDs not being in the upper or lower cases
                    selected_instrumentIDs.append(k)
        return selected_instrumentIDs
