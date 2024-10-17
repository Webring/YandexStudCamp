def command_bytes(device, control, data):
    return bytearray([0xff, device, control, data, 0xff])


def make_command(device, control, min=0, max=255):
    def command(data=0x00):
        if not (min <= data <= max):
            raise ValueError(f"data must be {min} <= data <= {max}")
        return command_bytes(device, control, data)

    return command


class RobotDevices:
    class Wheels:
        class Movement:
            DEVICE_ID = 0x00

            STOP_BYTE = 0x00
            FORWARD_BYTE = 0x01
            BACKWARD_BYTE = 0x02
            ROTATE_LEFT_BYTE = 0x03
            ROTATE_RIGHT_BYTE = 0x04

            forward = make_command(DEVICE_ID, FORWARD_BYTE)
            backward = make_command(DEVICE_ID, BACKWARD_BYTE)
            rotate_left = make_command(DEVICE_ID, ROTATE_LEFT_BYTE)
            rotate_right = make_command(DEVICE_ID, ROTATE_RIGHT_BYTE)
            stop = make_command(DEVICE_ID, STOP_BYTE)

        class Power:
            DEVICE_ID = 0x02

            MIN_POWER = 0
            MAX_POWER = 100

            LEFT_MOTOR = 0x01
            RIGHT_MOTOR = 0x02

            set_left_power = make_command(DEVICE_ID, LEFT_MOTOR, MIN_POWER, MAX_POWER)
            set_right_power = make_command(DEVICE_ID, RIGHT_MOTOR, MIN_POWER, MAX_POWER)

    class Servo:
        DEVICE_ID = 0x01

        MIN_ANGLE = 0
        MAX_ANGLE = 180

        SERVO_1 = 0x01
        SERVO_2 = 0x02
        SERVO_3 = 0x03
        SERVO_4 = 0x04
        SERVO_5 = 0x07
        SERVO_6 = 0x08

        set_servo_1 = make_command(DEVICE_ID, SERVO_1, MIN_ANGLE, MAX_ANGLE)
        set_servo_2 = make_command(DEVICE_ID, SERVO_2, MIN_ANGLE, MAX_ANGLE)
        set_servo_3 = make_command(DEVICE_ID, SERVO_3, MIN_ANGLE, MAX_ANGLE)
        set_servo_4 = make_command(DEVICE_ID, SERVO_4, MIN_ANGLE, MAX_ANGLE)
        set_servo_5 = make_command(DEVICE_ID, SERVO_5, MIN_ANGLE, MAX_ANGLE)
        set_servo_6 = make_command(DEVICE_ID, SERVO_6, MIN_ANGLE, MAX_ANGLE)

    class Led:
        DEVICE_ID = 0x06

        DISABLE = 0x00
        RED = 0x01
        GREEN = 0x02

        set_disabled = make_command(DEVICE_ID, DISABLE)
        set_red = make_command(DEVICE_ID, RED)
        set_green = make_command(DEVICE_ID, GREEN)



        catch_mode = make_command(0x03, 0x01)
        cruising_mode = make_command(0x03, 0x00)
