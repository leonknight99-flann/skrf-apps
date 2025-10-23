from qtpy import QtWidgets, QtCore

from skrf_qtwidgets import NetworkListWidget, NetworkPlotWidget, qt
from sql_qtwidgets import SQLDataSearchWidget


class TestDataViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Setup UI --- #
        self.resize(825, 775)
        self.setWindowTitle("Test Data Viewer")
        self.verticalLayout_main = QtWidgets.QVBoxLayout(self)

        self.vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self)
        size_policy_vert = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        size_policy_vert.setVerticalStretch(1)
        self.vsplitter.setSizePolicy(size_policy_vert)

        self.sql_widg = SQLDataSearchWidget(self.vsplitter)

        self.hsplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        size_policy_hori = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        size_policy_hori.setVerticalStretch(1)
        self.hsplitter.setSizePolicy(size_policy_hori)

        self.measurements_widget = QtWidgets.QWidget(self.hsplitter)
        self.measurements_widget_layout = QtWidgets.QVBoxLayout(self.measurements_widget)
        self.measurements_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.listWidget_measurements = NetworkListWidget(self.measurements_widget)

        self.evaluate_buttons = self.listWidget_measurements.get_import_buttons()
        self.save_buttons = self.listWidget_measurements.get_save_buttons()
        self.measurements_widget_layout.addWidget(self.evaluate_buttons)
        self.measurements_widget_layout.addWidget(self.listWidget_measurements)
        self.measurements_widget_layout.addWidget(self.save_buttons)

        self.ntwk_plot = NetworkPlotWidget(self.hsplitter)
        self.ntwk_plot.corrected_data_enabled = False

        self.vsplitter.addWidget(self.hsplitter)

        self.verticalLayout_main.addWidget(self.vsplitter)
        self.hsplitter.setStretchFactor(1, 100)  # important that this goes at the end
        self.vsplitter.setStretchFactor(1, 100)  # important that this goes at the end
        # --- END SETUP UI --- #

        self.listWidget_measurements.ntwk_plot = self.ntwk_plot
        self.listWidget_measurements.sql_widg = self.sql_widg

def main():
    qt.single_widget_application(TestDataViewer, appid="TestDataViewer", icon='C:\\Users\\lkni\\Documents\\Code Files\\scikit-rf GIT and APP\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\images\\FlannMicrowave.ico')#='.\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\images\\FlannMicrowave.ico')



if __name__ == "__main__":
    main()
