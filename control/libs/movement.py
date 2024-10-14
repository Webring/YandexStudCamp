from BaseRobotHardware import BaseRobotHardware
from control.libs.commands import RobotDevices


class Movement(BaseRobotHardware):
    MOTOR_MAX = 100
    MOTOR_MIN = 40

    def forward(self):
        self._send(RobotDevices.Wheels.Movement.forward())

    def rotate_left(self):
        self._send(RobotDevices.Wheels.Movement.rotate_left())

    def rotate_right(self):
        self._send(RobotDevices.Wheels.Movement.rotate_right())

    def backward(self):
        self._send(RobotDevices.Wheels.Movement.backward())

    def stop(self):
        self._send(RobotDevices.Wheels.Movement.stop())

    def set_left_power(self, value:int):
        value = max(self.MOTOR_MIN, min(self.MOTOR_MAX, value))
        self._send(RobotDevices.Wheels.Power.set_left_power(value))

    def set_right_power(self, value: int):
        value = max(self.MOTOR_MIN, min(self.MOTOR_MAX, value))
        self._send(RobotDevices.Wheels.Power.set_right_power(value))

    def set_power(self, value: int):
        self.set_left_power(value)
        self.set_right_power(value)
