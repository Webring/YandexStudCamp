from control.libs.BaseRobotHardware import BaseRobotHardware
from control.libs.commands import RobotDevices

class Sensors(BaseRobotHardware):
    def _send_and_recieve(self, command:bytearray):
        self.socket.sendall(command)
        return self.socket.recv(1024)

    def get_infrared_data(self):
        return list(self._send_and_recieve(RobotDevices.Sensors.get_infrared()))
    
    def get_ultrasonic_data(self):
        return self._send_and_recieve(RobotDevices.Sensors.get_ultrasonic())