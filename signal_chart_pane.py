import matplotlib
matplotlib.use('Qt5Agg')  # ← важно!

from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class SignalChartPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tick = 0

        # Настройка графика
        self.figure = Figure(figsize=(9, 2))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Данные для графиков
        self.signal_data = []
        self.downlink_data = []
        self.uplink_data = []
        self.x_data = []

        # Настройки графика
        self.ax.set_title("Сигнал и связь")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Значение")

        # Визуализация
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, signal_strength, downlink, uplink):
        # Ограничиваем количество точек (окно из 100 точек)
        if len(self.x_data) > 100:
            self.x_data.pop(0)
            self.signal_data.pop(0)
            self.downlink_data.pop(0)
            self.uplink_data.pop(0)

        # Добавляем новые данные
        self.x_data.append(self.tick)
        self.signal_data.append(signal_strength)
        self.downlink_data.append(downlink)
        self.uplink_data.append(uplink)
        self.tick += 1

        # Обновляем график
        self.ax.clear()
        self.ax.plot(self.x_data, self.downlink_data, label='Передатчик')
        self.ax.plot(self.x_data, self.uplink_data, label='Приемник')
        self.ax.legend()  # <-- Теперь legend() вызывается после добавления линий
        self.ax.set_title("Скорость передачи")
        self.ax.set_xlabel("Время")
        # self.ax.set_ylabel("Значение")
        self.ax.grid(True)
        self.canvas.draw()