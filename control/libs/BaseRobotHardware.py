class BaseRobotHardware:
    def __init__(self, socket):
        self.socket = socket

    def change_socket(self, new_socket):
        self.socket.close()
        self.socket = new_socket

    def _send(self, command: bytearray):
        self.socket.sendall(command)