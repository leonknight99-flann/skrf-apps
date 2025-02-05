from qtpy import QtCore, QtWidgets

from skrf_qtwidgets import NetworkPlotWidget, qt, NetworkCreateWidget

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

        self.create_network_widget = NetworkCreateWidget(self.splitter)

        self.ntwk_plot = NetworkPlotWidget(self.splitter)
        self.ntwk_plot.corrected_data_enabled = False

        self.verticalLayout_main.addWidget(self.splitter)
        self.splitter.setStretchFactor(1, 100)  # important that this goes at the end

        self.create_network_widget.ntwk_plot = self.ntwk_plot
        
        # --- END SETUP UI --- #


def main():
    qt.single_widget_application(Chimp, splash_screen=False, appid="ChimpSKRF", icon='.\\skrf-apps\\skrf_qtapps\\skrf_qtwidgets\\images\\FlannMicrowave.ico')

if __name__ == "__main__":
    main()
