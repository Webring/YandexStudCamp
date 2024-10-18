from control.libs.BaseRobotHardware import BaseRobotHardware
from control.libs.commands import RobotDevices


class Movement(BaseRobotHardware):
    MOTOR_MAX = 100
    MOTOR_MIN = 15

    def forward(self, delay = 0):
        t = RobotDevices.Wheels.Movement.forward(delay)
        self._send(t)

    def rotate_left(self, delay = 0):
        self._send(RobotDevices.Wheels.Movement.rotate_left(delay))

    def rotate_right(self, delay = 0):
        self._send(RobotDevices.Wheels.Movement.rotate_right(delay))

    def backward(self, delay = 0):
        self._send(RobotDevices.Wheels.Movement.backward(delay))

    def stop(self, delay = 0):
        self._send(RobotDevices.Wheels.Movement.stop(delay))

    def set_left_power(self, value:int):
        value = max(self.MOTOR_MIN, min(self.MOTOR_MAX, value))
        self._send(RobotDevices.Wheels.Power.set_left_power(value))

    def set_right_power(self, value: int):
        value = max(self.MOTOR_MIN, min(self.MOTOR_MAX, value))
        self._send(RobotDevices.Wheels.Power.set_right_power(value))

    def set_power(self, value: int):
        self.set_left_power(value)
        self.set_right_power(value)
