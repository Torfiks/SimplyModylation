import sys
from PyQt5.QtWidgets import QApplication, QScrollArea, QMainWindow

from train_simulator_ui import TrainSimulatorUI


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Моделирование поезда и базовых станций")
        self.setGeometry(100, 100, 1200, 700)

        scroll_area = QScrollArea()
        content_widget = TrainSimulatorUI()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)

        self.setCentralWidget(scroll_area)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())