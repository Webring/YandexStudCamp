from BaseRobotHardware import BaseRobotHardware
from commands import RobotDevices


class Claw(BaseRobotHardware):
    CLENCH_ANGLE = 40
    UNCLECH_ANGLE = 100

    def сlench(self):
        self._send(RobotDevices.Servo.set_servo_4(self.CLENCH_ANGLE))

    def unclench(self):
        self._send(RobotDevices.Servo.set_servo_4(self.UNCLECH_ANGLE))

    def set(self, value: int):
        self._send(RobotDevices.Servo.set_servo_4(max(self.CLENCH_ANGLE, min(self.UNCLECH_ANGLE, value))))


class CameraMount(BaseRobotHardware):
    MIN_HORIZONTAL_ANGLE = 0
    HORIZONTAL_CENTER_ANGLE = 90
    MAX_HORIZONTAL_ANGLE = 180

    MIN_VERTICAL_ANGLE = 65
    VERTICAL_CENTER_ANGLE = 90
    MAX_VERTICAL_ANGLE = 180


    def set_horizontal(self, value):
        self._send(RobotDevices.Servo.set_servo_5(value))

    def set_vertical(self, value):
        self._send(RobotDevices.Servo.set_servo_6(value))

    def horizontal_center(self):
        self.set_horizontal(self.CENTER_HORIZONTAL_ANGLE)

    def vertical_center(self):
        self.set_horizontal(self.CENTER_VERTICAL_ANGLE)

