import numpy as np
from led import Led
from camera_yolo import state

from socket import *
import time

from movement import Movement


host = "192.168.2.157"
port = 2001

delta = 0.1
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
led = Led(sock)
move = Movement(sock)


def distanse(point_a, point_b):
    x_a, y_a = point_a
    x_b, y_b = point_b
    return np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)


import math


def calculate_angle(point_a, point_b, point_c):
    x1, y1 = point_a
    x2, y2 = point_b
    x3, y3 = point_c

    AB = (x2 - x1, y2 - y1)
    AC = (x3 - x1, y3 - y1)

    dot_product = AB[0] * AC[0] + AB[1] * AC[1]

    AB_length = math.sqrt(AB[0] ** 2 + AB[1] ** 2)
    AC_length = math.sqrt(AC[0] ** 2 + AC[1] ** 2)

    cos_alpha = dot_product / (AB_length * AC_length)

    alpha = math.acos(cos_alpha)

    if (x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1) > 0:
        return alpha
    else:
        return -alpha

def robot_position():
    robot_state = state()
    print(robot_state, 'aaaaa')
    if len(robot_state[4]) * len(robot_state[2]) != 0:
        for p in robot_state[2]:
            if distanse(robot_state[4][-1], p) < 200:
                return robot_state[4][-1], p
            else:
                print("Робота/Клешни нет")
                return robot_position()
    else:
        print("Ничего нет")
        return robot_position()

def in_epsilon_area(point, eps=100):
    point_robot, point_claw = robot_position()
    if distanse(point, point_robot) <= eps:
        return True
    else:
        return False


def start():
    led.set_red()
    move.set_power(16)


def rotate(point_b):
    point_robot, point_claw = robot_position()
    cur_angle = calculate_angle(point_robot, point_claw, point_b)
    print(cur_angle)
    while (-delta >= cur_angle) or (cur_angle >= delta):
        print(robot_position())
        point_robot, point_claw = robot_position()
        cur_angle = calculate_angle(point_robot, point_claw, point_b)
        print(cur_angle)
        if cur_angle > delta:
            move.rotate_right()
            time.sleep(0.1)
        elif cur_angle < -delta:
            move.rotate_left()
            time.sleep(0.1)
        else:
            return


def go_forward(point_b):
    move.set_power(40)
    while not in_epsilon_area(point_b):
        move.forward()
        time.sleep(3)


def main():
    point_stack = [(1476, 556)]
    start()
    for i in point_stack:
        rotate(i)
        move.stop()
        print("go forward")
        go_forward(i)


main()
