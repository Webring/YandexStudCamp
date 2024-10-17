from socket import *
import time
from movement import Movement
from video_detection import send_coordinates
from manipulator import Claw, Servo
from math import atan
host = "192.168.2.157"
port = 2001

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
move = Movement(sock)
move.set_power(30)
clw = Claw(sock)
delta = 0.07
flag = False

def move_to_cube():
    while True:
        state = send_coordinates()
        if 0 in state.keys():
            move.forward()
        else:
            move.stop()
            break
    


def catch():
    state = send_coordinates()
    if (0 in state.keys()) and (5 in state.keys()):
        claw = state[0]
        target = state[5]
    else:
        print('Робот не видит')
        return
    angle = calculate_angle(claw, target)
    while (-delta + 0.65 >= angle) or (angle >= delta + 0.65):
        state = send_coordinates()
        if (0 in state.keys()) and (5 in state.keys()):
            claw = state[0]
            target = state[5]
        else:
            print('Робот не видит')
            return
        angle = calculate_angle(claw, target)
        print(angle)
        if angle > delta + 0.65:
            move.rotate_left()
        else:
            move.rotate_right()
    move_to_cube()

def calculate_angle(claw, target):
    x_s, y_s = target
    x_e, y_e = claw
    return atan((max(x_s, x_e) - min(x_s, x_e)) / (max(y_s, y_e) - min(y_s, y_e)))

def catchCube():
    move.forward()
    time.sleep(0.1)
    clw.сlench()

clw.unclench()