from socket import *
import time
from video_parser import send_coordinates
from control.libs.movement import Movement
from control.libs.manipulator import Claw, Servo
from control.libs.sensors import Sensors
from math import atan

host = "192.168.21.171"
port = 2001

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
move = Movement(sock)
clw = Claw(sock)
man = Servo(sock)
sensors = Sensors(sock)
delta = 0.8
cought = False
last = None

default_marker = None


def move_to_t(target):
    global default_marker
    global delta
    print(send_coordinates())
    move.set_power(25)
    move.set_left_power(30)
    default_marker = (150, 137)
    if target in [3, 4]:
        man.basket_mode()
        click(target)
    elif target == 2:
        man.basket_mode()
        deliver_to_basket(target)


def allign_self(target):
    global last
    print(delta)
    try:
        angle = calculate_angle(send_coordinates()[target])
    except KeyError:
        if last=="left":
            move.rotate_right(6)
        else:
            move.rotate_left(6)
        return 
    print(angle)
    if angle > delta:
        move.rotate_right(6)
        last = "right"
    elif angle < delta:
        move.rotate_left(6)
        last = "left"
    print(last)


def calculate_angle(target):
    x_s, y_s = target
    x_e, y_e = default_marker
    return atan((max(x_s, x_e) - min(x_s, x_e)) / (max(y_s, y_e) - min(y_s, y_e)))

def click(target):
    while not sensors.get_infrared_data()[0] and not sensors.get_infrared_data()[2]:
        print("alligning")
        allign_self(target)
        time.sleep(8*0.05)
        print("moving")
        move.forward(30)
        time.sleep(31*0.05)
        print(sensors.get_infrared_data())
    move.stop()
    man.set(2, 180)
    man.set(3, 180)
    time.sleep(0.2)
    man.set(2, 80)
    time.sleep(2)
    man.basket_mode()

def deliver_to_basket(target):
    print(sensors.get_infrared_data())
    while not sensors.get_infrared_data()[0] and not sensors.get_infrared_data()[2]:
        print("alligning")
        allign_self(target)
        time.sleep(8*0.05)
        print("forward")
        move.forward(15)
        time.sleep(16*0.05)
    if cought:
        clw.unclench()

move_to_target(4)
# cought = True
# time.sleep(2)
# move_to_target(2)