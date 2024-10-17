from BaseRobotHardware import BaseRobotHardware
from commands import RobotDevices

servo_dict = {
    1: RobotDevices.Servo.set_servo_1,
    2: RobotDevices.Servo.set_servo_2,
    3: RobotDevices.Servo.set_servo_3,
    4: RobotDevices.Servo.set_servo_4,
    5: RobotDevices.Servo.set_servo_5,
    6: RobotDevices.Servo.set_servo_6
              }

class Claw(BaseRobotHardware):
    CLENCH_ANGLE = 40
    UNCLECH_ANGLE = 100

    def сlench(self):
        self._send(RobotDevices.Servo.set_servo_4(self.CLENCH_ANGLE))

    def unclench(self):
        self._send(RobotDevices.Servo.set_servo_4(self.UNCLECH_ANGLE))

    def set(self, value: int):
        self._send(RobotDevices.Servo.set_servo_4(max(self.CLENCH_ANGLE, min(self.UNCLECH_ANGLE, value))))

class Servo(BaseRobotHardware):
    def __init__(self, socket):
        super().__init__(socket)
    
    def set(self, servo_num: int, value: int):
        self._send(servo_dict[servo_num](value))

    def catch_mode(self):
        self._send(RobotDevices.Servo.catch_mode())
    
    def cruising_mode(self):
        self._send(RobotDevices.Servo.cruising_mode())

class CameraMount(BaseRobotHardware):
    MIN_HORIZONTAL_ANGLE = 0
    HORIZONTAL_CENTER_ANGLE = 95
    MAX_HORIZONTAL_ANGLE = 180

    MIN_VERTICAL_ANGLE = 65
    VERTICAL_CENTER_ANGLE = 90
    MAX_VERTICAL_ANGLE = 180


    def set_horizontal(self, value):
        self._send(RobotDevices.Servo.set_servo_5(value))

    def set_vertical(self, value):
        self._send(RobotDevices.Servo.set_servo_6(value))

    def horizontal_center(self):
        self.set_horizontal(self.HORIZONTAL_CENTER_ANGLE)

    def vertical_center(self):
        self.set_horizontal(self.VERTICAL_CENTER_ANGLE)

