from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QSlider,
    QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt

# Импортируем ранее написанные компоненты
from simulation_pane import SimulationPane
from signal_chart_pane import SignalChartPane


class TrainSimulatorUI(QWidget):
    def __init__(self):
        super().__init__()

        self.simulation_pane = SimulationPane()
        self.signal_chart_pane = SignalChartPane()

        # Поля ввода
        self.base_stations_field = QLineEdit("5") # количество базовых станций 
        self.distance_field = QLineEdit("100") # расстояние между бс

        # Слайдер скорости
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(350)
        self.speed_slider.setValue(300)
        self.tick_labels_layouts = QGridLayout()

        # Метка скорости
        self.current_speed_label = QLabel(f"Скорость поезда: {self.speed_slider.value()} км/ч")
        self.speed_slider.valueChanged.connect(self.update_speed_label)

        # Кнопки
        self.start_button = QPushButton("Запустить симуляцию")
        self.toggle_button = QPushButton("Остановить симуляцию")

        # Лейблы для вывода данных
        self.downlink_label = QLabel("Downlink: 0 Mbps")
        self.uplink_label = QLabel("Uplink: 0 Mbps")

        # Установка стилей
        self.downlink_label.setStyleSheet("font-size: 16px;")
        self.uplink_label.setStyleSheet("font-size: 16px;")

        # Обработчики событий
        self.start_button.clicked.connect(self.start_simulation)
        self.toggle_button.clicked.connect(self.toggle_simulation)

        # Компоновка элементов
        self.init_ui()

        # Передаем ссылку на себя в SimulationPane для обратной связи
        self.simulation_pane.set_app(self)
        self.start_simulation()
        self.simulation_pane.stop_animation()
        self.toggle_button.setText("Остановить симуляцию")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Верхняя панель управления
        control_layout = QGridLayout()

        control_layout.addWidget(QLabel("Количество БС:"), 0, 0)
        control_layout.addWidget(self.base_stations_field, 0, 1)
        control_layout.addWidget(QLabel("Расстояние между БС (км):"), 0, 2)
        control_layout.addWidget(self.distance_field, 0, 3)
        control_layout.addWidget(self.start_button, 0, 4)

        control_layout.addWidget(QLabel("Скорость поезда:"), 1, 0)
        control_layout.addWidget(self.speed_slider, 1, 1, 1, 3)
        control_layout.addWidget(self.current_speed_label, 1, 4)

        # Добавляем в основную сетку под слайдер
        self.tick_labels_layout()
        control_layout.addLayout(self.tick_labels_layouts, 2, 1, 1, 3)  # строка 2, колонки 1-3

        control_layout.addWidget(self.toggle_button, 3, 4)
        control_layout.addWidget(QLabel(self.current_speed_label.text()), 3, 0, 1, 4)
        control_layout.addWidget(self.downlink_label, 4, 0, 1, 5)
        control_layout.addWidget(self.uplink_label, 5, 0, 1, 5)

        layout.addLayout(control_layout)

        # Панель симуляции
        layout.addWidget(self.simulation_pane)

        # График
        layout.addWidget(self.signal_chart_pane)

        self.setLayout(layout)

    def start_simulation(self):
        try:
            num_stations = int(self.base_stations_field.text())
            station_distance = float(self.distance_field.text())

            self.simulation_pane.start_simulation(num_stations, station_distance)
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите корректные числа.")


    def tick_labels_layout(self):
        ticks = [0, 50, 100, 150, 200, 250, 300, 350]

        for col, value in enumerate(ticks):
            label = QLabel(str(value))
            label.setAlignment(Qt.AlignCenter)
            self.tick_labels_layouts.addWidget(label, 0, col)

        # Уменьшаем расстояние между метками
        self.tick_labels_layouts.setHorizontalSpacing(0)
        self.tick_labels_layouts.setContentsMargins(0, 0, 0, 0)

    def update_speed_label(self):
        speed = self.speed_slider.value()
        self.current_speed_label.setText(f"Скорость поезда: {speed} км/ч")

    def get_current_speed(self):
        return self.speed_slider.value()

    def toggle_simulation(self):
        self.simulation_pane.toggle_animation()
        self.toggle_button.setText("Остановить симуляцию" if self.simulation_pane.is_running() else "Продолжить симуляцию")

    def update_links(self, signal_strength, downlink, uplink):
        self.downlink_label.setText(f"Downlink: {round(downlink, 4)} Mbps")
        self.uplink_label.setText(f"Uplink: {round(uplink, 4)} Mbps") # :.2f
        self.signal_chart_pane.update_plot(signal_strength, downlink, uplink)