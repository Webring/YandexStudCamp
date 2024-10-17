from BaseRobotHardware import BaseRobotHardware
from commands import RobotDevices


class Led(BaseRobotHardware):
    def set_green(self):
        self._send(RobotDevices.Led.set_green())

    def set_red(self):
        self._send(RobotDevices.Led.set_red())

    def disable(self):
        self._send(RobotDevices.Led.set_disabled())