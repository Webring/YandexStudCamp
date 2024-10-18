from socket import *
import time
from video_parser import send_coordinates
from movement import Movement
from manipulator import Claw, Servo
from math import atan

host = "192.168.2.157"
port = 2001

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
move = Movement(sock)
clw = Claw(sock)
man = Servo(sock)
delta = 0.07
alpha_0 = 0.15
upper_alpha = 0.89
flag = False


def start():
    move.set_power(15)
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
        if cnt_frames % 3 == 0:
            print("#########\nI need to catch\n########")
            catch(object, target_angle)
        if target in state.keys():
            cnt = 0
            move.forward()
        else:
            cnt += 1
            move.forward()
        if cnt == 2:
            move.stop()
            break


def catch(object, target_angle):
    move.set_power(15)
    man.catch_mode()
    clw.unclench()
    state = send_coordinates()
    if (object in state.keys()) and (5 in state.keys()):
        claw = state[object]
        target = state[5]
    else:
        print('Робот не видит')
        return
    angle = calculate_angle(claw, target)
    while (-delta + target_angle >= angle) or (angle >= delta + target_angle):
        state = send_coordinates()
        if (object in state.keys()) and (5 in state.keys()):
            claw = state[object]
            target = state[5]
        else:
            print('Робот не видит')
            return
        angle = calculate_angle(claw, target)
        if angle > delta + target_angle:
            move.rotate_left()
        else:
            move.rotate_right()


def calculate_angle(claw, target):
    x_s, y_s = target
    x_e, y_e = claw
    return atan((max(x_s, x_e) - min(x_s, x_e)) / (max(y_s, y_e) - min(y_s, y_e)))


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
