from socket import *
import time
from video_parser import send_coordinates
from movement import Movement
from manipulator import Claw, Servo
from math import atan
from sensors import Sensors
import numpy as np
host = "192.168.21.171"
port = 2001

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
move = Movement(sock)
clw = Claw(sock)
man = Servo(sock)
sns = Sensors(sock)
delta = 0.07
alpha_0 = 0.53
upper_alpha = -0.91
flag = False


def start():
    move.set_power(25)
    clw.clench()
    man.cruising_mode()


def move_to_target(object, target_angle):
    catch(object, target_angle)
    move.set_power(25)
    cnt = 0
    cnt_frames = 0
    while True:
        cnt_frames += 1
        state = send_coordinates()
        datchik = sns.get_infrared_data()
        if cnt_frames % 2 == 0:
            print("#########\nI need to catch\n########")
            catch(object, target_angle)
        if object in state.keys():
            cnt = 0
            move.forward()
        else:
            cnt += 1
            move.forward()
        if datchik[1] == 1:
            print(datchik)
            move.stop()
            break


def catch(object, target_angle):
    move.set_power(25)
    man.catch_mode()
    clw.unclench()
    state = send_coordinates()
    if (object in state.keys()) and (5 in state.keys()):
        claw = state[object]
        target = state[5]
    else:
        return
    angle = calculate_angle(claw, target)
    print(angle)
    while (-delta + target_angle >= angle) or (angle >= delta + target_angle):
        state = send_coordinates()
        if (object in state.keys()) and (5 in state.keys()):
            claw = state[object]
            target = state[5]
        else:
            return
        angle = calculate_angle(claw, target)
        print(angle)
        if angle > delta + target_angle:
            move.rotate_right()
        else:
            move.rotate_left()


def calculate_angle(claw, target):
    x_s, y_s = target
    x_e, y_e = claw
    return np.abs((np.arctan((x_e - x_s) / (0.00001 + y_e - y_s))))


def lift():
    move.set_power(20)
    man.catch_mode()
    clw.unclench()
    move.forward()
    time.sleep(0.2)
    move.stop()
    clw.clench()
    print('Объект захвачен')
    man.cruising_mode()


target = 0

start()
move_to_target(target, alpha_0)
lift()

time.sleep(1)

'''clw.unclench()'''
man.basket_mode()
