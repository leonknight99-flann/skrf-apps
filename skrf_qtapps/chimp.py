from qtpy import QtCore, QtWidgets

from skrf_qtwidgets import NetworkPlotWidget, qt, CreateNetworkWidget

class Chimp(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Setup UI --- #
        self.resize(825, 575)
        self.setWindowTitle("Chimp Scikit-RF")
        self.verticalLayout_main = QtWidgets.QVBoxLayout(self)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        size_policy.setVerticalStretch(1)
        self.splitter.setSizePolicy(size_policy)

        self.create_network_widget = CreateNetworkWidget(self)

        self.ntwk_plot = NetworkPlotWidget(self)
        self.ntwk_plot.corrected_data_enabled = False

        self.splitter.addWidget(self.create_network_widget)
        self.splitter.addWidget(self.ntwk_plot)

        self.verticalLayout_main.addWidget(self.splitter)
        self.splitter.setStretchFactor(1, 100)  # important that this goes at the end
        
        # --- END SETUP UI --- #


def main():
    qt.single_widget_application(Chimp, appid="ChimpSKRF")

if __name__ == "__main__":
    main()
