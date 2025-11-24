from time import time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QTimer

class BaseStation:
    def __init__(self, position, x):
        self.position = position  # логическая позиция (км)
        self.x = x                # пиксельная позиция на экране
        self.pixmap = None

    def get_x(self):
        return self.x

    def set_x(self, x):
        self.x = x

    def load_image(self, path="images/base_station.png", size=(30, 30)):
        self.pixmap = QPixmap(path).scaled(*size, Qt.KeepAspectRatio)

class SimulationPane(QWidget):

    DESIRED_WIDTH = 50
    DESIRED_HEIGHT = 30
    BASE_STATION_WIDTH = 30
    BASE_STATION_HEIGHT = 30

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragged_station = None
        self.width = 900
        self.setFixedSize(self.width, 200)

        # Поезд и его изображение
        self.train_position = 0     # физическое положение (км)
        self.total_track_length = 100_000_000 # общая длина пути (км)
        self.train_pixmap = QPixmap("images/train.png").scaled(
            self.DESIRED_WIDTH, self.DESIRED_HEIGHT, Qt.KeepAspectRatio
        )
        self.dragging_train = False
        self.drag_start_x = 0

        # Станции
        self.stations = []

        # Таймер анимации
        self.running = False
        self.last_update_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        # Загрузка изображений станций
        for station in self.stations:
            station.load_image()

        # Для связи с UI
        self.app = None  # внешний контроллер (TrainSimulatorUI)

    def start_simulation(self, num_stations, station_distance):
        # Очистка предыдущих станций
        self.stations.clear()

        spacing = 900.0 / (num_stations - 1)
        for i in range(num_stations):
            position = station_distance * i
            x = int(spacing * i)
            station = BaseStation(position, x)
            station.load_image()
            self.stations.append(station)

        self.total_track_length = station_distance * (num_stations - 1)

        self.train_position = 0
        self.running = True
        self.last_update_time = 0

        self.timer.start(50)
        self.update()  # принудительная перерисовка

    def is_running(self):
        return self.running

    def set_app(self, app):
        """ Для обратной связи с основным интерфейсом"""
        self.app = app

    def stop_animation(self):
        self.running = False

    def toggle_animation(self):
        self.running = not self.running

    def mousePressEvent(self, event):
        """Проверяет, нажал ли пользователь на поезд или станцию."""
        mouseX = event.x()
        mouseY = event.y()

        scale = self.width / self.total_track_length
        trainX = int(self.train_position * scale)

        # Проверяем, нажали ли на поезд
        if (abs(mouseX - trainX) <= self.DESIRED_WIDTH // 2 and
                abs(mouseY - 70) <= self.DESIRED_HEIGHT // 2):
            self.dragging_train = True
            self.drag_start_x = mouseX - trainX
            return

        # Проверяем, нажали ли на станцию
        for station in self.stations:
            x = station.get_x()
            if (abs(mouseX - x) <= self.BASE_STATION_WIDTH // 2 and
                    abs(mouseY - 85) <= self.BASE_STATION_HEIGHT // 2):
                self.dragged_station = station
                self.drag_start_x = mouseX - x
                break

    def mouseReleaseEvent(self, event):
        """Освобождает поезд или станцию после отпускания кнопки мыши."""
        self.dragging_train = False
        self.dragged_station = None

    def mouseMoveEvent(self, event):
        """Если поезд или станция "захвачены" — двигает их мышкой."""
        mouseX = event.x()

        if self.dragging_train:
            scale = self.total_track_length / 900.0
            new_x_pixel = mouseX - self.DESIRED_WIDTH // 2
            self.train_position = max(0, min(self.total_track_length, (new_x_pixel * scale)))
            self.update()

        elif hasattr(self, 'dragged_station') and self.dragged_station:
            self.dragged_station.set_x(mouseX - self.drag_start_x)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рельсы
        painter.setPen(Qt.gray)
        painter.drawLine(0, 100, self.width, 100)

        # Базовые станции
        for station in self.stations:
            x = station.get_x()
            if station.pixmap:
                painter.drawPixmap(x - self.BASE_STATION_WIDTH // 2, 85, station.pixmap)
            else:
                painter.setBrush(Qt.blue)
                painter.drawEllipse(x - 8, 92, 16, 16)

        # Поезд
        scale = 900.0 / self.total_track_length
        trainX = int(self.train_position * scale)

        if self.train_pixmap:
            if self.dragging_train:
                # Рисуем белое свечение вокруг поезда
                painter.setPen(QColor(255, 255, 255, 150))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(
                    trainX - 10 - 2, 70 - 2, 24, 24
                )

            painter.drawPixmap(trainX - self.DESIRED_WIDTH // 2, 60,
                               self.train_pixmap)
        else:
            if self.dragging_train:
                painter.setBrush(Qt.yellow)
            else:
                painter.setBrush(Qt.red)
            painter.drawEllipse(trainX - 10, 70, 20, 20)

        # Расчёт сигнала
        total_signal = self.calculate_total_signal_strength(trainX)
        downlink = min(100, total_signal * 20)
        uplink = min(50, total_signal * 10)

        if self.app:
            self.app.update_links(total_signal, downlink, uplink)

    def calculate_total_signal_strength(self, train_x):
        signal = 0
        for station in self.stations:
            distance = abs(station.get_x() - train_x)
            signal += 1 / (0.1 + 0.01 * distance)
        return signal

    def update_animation(self):
        if not self.running:
            return

        current_time =  int((time()) * 1000)

        if self.last_update_time == 0:
            self.last_update_time = current_time
            return

        dt = (current_time - self.last_update_time) / 1000.0  # секунды
        speed_kmph = self.app.get_current_speed() if self.app else 300
        self.train_position += (speed_kmph / 3.6) * dt  # м/с

        if self.train_position > self.total_track_length:
            self.train_position = 0

        self.last_update_time = current_time
        self.update()  # вызывает paintEvent