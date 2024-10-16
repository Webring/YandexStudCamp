import json
import sys
import socket

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QSlider, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSlot, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import traceback

from control.libs.movement import Movement


def socket_send(current_socket: socket.socket, data: bytearray):
    if current_socket:
        try:
            current_socket.sendall(data)
            return f"send data: {data}"
        except socket.error as e:
            return f"Failed to send data: {e}"
    return "Socket not connected"

class SliderData:
    def __init__(self, array: bytearray, index: int, min_value: int, max_value: int, title: str,
                 start_value: int = None):
        self.array = bytearray(array)
        self.index = index
        self.title = title
        self.max = max_value
        self.min = min_value
        self.start_value = start_value if start_value is not None else min_value


class ClientWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XiaR robot control")

        # Центральный виджет
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Основной макет
        self.layout = QVBoxLayout(self.central_widget)

        # Поля для ввода IP и порта
        self.ip_label = QLabel("IP Адрес:")
        self.ip_input = QLineEdit()
        self.port_label = QLabel("Порт:")
        self.port_input = QLineEdit()

        # Кнопка подключения и индикатор подключения
        self.connect_button = QPushButton("Подключиться")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.connection_status = QLabel("Не подключено")

        # Поле iframe для отображения веб-страницы по IP:8081
        self.web_view = QWebEngineView()

        # Макет для слайдеров
        self.slider_layout = QGridLayout()

        # Подключение элементов интерфейса
        self.init_ui()

        try:
            with open("last_data.json", mode="r", encoding="utf-8") as file:
                data = json.load(file)
                self.ip_input.setText(data["ip"])
                self.port_input.setText(str(data["port"]))
        except FileNotFoundError:
            self.statusBar().showMessage("Предыдушие данные не найдены!")

        self.sock = None
        self.pressed_keys = set()

    def keyPressEvent(self, event: QKeyEvent):
        scan_code = event.nativeScanCode()
        self.pressed_keys.add(scan_code)

        if self.sock:
            movement = Movement(self.sock)
            if scan_code == 17:
                movement.forward()
            elif scan_code == 30:
                movement.rotate_right()
            elif scan_code == 32:
                movement.rotate_left()
            elif scan_code == 31:
                movement.backward()

    def keyReleaseEvent(self, event=None):
        scan_code = event.nativeScanCode()
        try:
            self.pressed_keys.discard(scan_code)
        except Exception as e:
            print(Exception, "not found key", scan_code)
        if len(set([17, 30, 31, 32]) & self.pressed_keys) == 0 and self.sock:
            try:
                data = bytearray([0xff, 0x00, 0x00, 0x00, 0xff])
                self.sock.sendall(data)
                print(f"Sent data: {data}")
            except socket.error as e:
                print(f"Failed to send data: {e}")

    def init_ui(self):
        # Настройка макета для полей ввода IP и порта
        ip_port_layout = QHBoxLayout()
        ip_port_layout.addWidget(self.ip_label)
        ip_port_layout.addWidget(self.ip_input)
        ip_port_layout.addWidget(self.port_label)
        ip_port_layout.addWidget(self.port_input)
        ip_port_layout.addWidget(self.connect_button)
        ip_port_layout.addWidget(self.connection_status)

        self.layout.addLayout(ip_port_layout)
        self.layout.setStretch(0, 0)

        # Веб-страница через iframe
        self.layout.addWidget(self.web_view)
        self.layout.setStretch(1, 1)

        # Добавляем несколько слайдеров
        sliders_data = [
            SliderData([0xff, 0x01, 0x01, 0x00, 0xff], 3, 0, 180, "Плечо", 180),
            SliderData([0xff, 0x01, 0x02, 0x00, 0xff], 3, 0, 180, "Локоть", 180),
            SliderData([0xff, 0x01, 0x03, 0x00, 0xff], 3, 0, 180, "Поворот"),
            SliderData([0xff, 0x01, 0x04, 0x00, 0xff], 3, 0, 180, "Захват"),
            SliderData([0xff, 0x01, 0x07, 0x00, 0xff], 3, 0, 180, "Поворот камеры"),
            SliderData([0xff, 0x01, 0x08, 0x00, 0xff], 3, 0, 180, "Высота камеры"),
            SliderData([0xff, 0x02, 0x01, 0x00, 0xff], 3, 0, 100, "Двигатель 1", 100),
            SliderData([0xff, 0x02, 0x02, 0x00, 0xff], 3, 0, 100, "Двигатель 2", 100),
        ]
        for i, sd in enumerate(sliders_data):
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(sd.min)
            slider.setMaximum(sd.max)
            slider.setValue(sd.start_value)
            slider.valueChanged.connect(self.create_handle(sd))

            self.slider_layout.addWidget(QLabel(sd.title), i, 0)
            self.slider_layout.addWidget(slider, i, 1)

        self.layout.addLayout(self.slider_layout)
        self.layout.setStretch(2, 0)

    def create_handle(self, sd):
        byte_set = sd.array
        index = sd.index
        def handle_change(value):
            if self.sock:
                # Изменяем набор байтов в соответствии с индексом и значением слайдера
                data = bytearray(byte_set)
                data[index] = value
                self.statusBar().showMessage(f"{sd.title} установлено значение {value}")
                try:
                    self.sock.sendall(data)
                    print(f"Sent data: {data}")
                except socket.error as e:
                    print(f"Failed to send data: {e}")

        return handle_change

    @pyqtSlot()
    def connect_to_server(self):
        ip = self.ip_input.text()
        try:
            port = int(self.port_input.text())
        except ValueError:
            self.connection_status.setText("Bad port")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            self.connection_status.setText("Подключено")
            self.statusBar().showMessage("Подключено к серверу")

            # Обновляем iframe на веб-страницу по IP и порту 8081
            self.web_view.setUrl(QUrl(f"http://{ip}:8081"))

            last_ip = {
                "ip": ip,
                "port": port
            }
            with open("last_data.json", mode="w", encoding="utf-8") as file:
                json.dump(last_ip, file)

        except socket.error as e:
            self.connection_status.setText("Ошибка подключения")
            print(f"Failed to connect: {e}")


def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    sys.exit(1)


sys.excepthook = excepthook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_widget = ClientWidget()
    client_widget.show()
    sys.exit(app.exec_())
