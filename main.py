from object_detection.video_parser import send_coordinates
from control.libs.manipulator import Claw, Servo
from socket import *
from catch import start, move_to_target, lift
from move import move_to_t
import time

host = "192.168.2.157"
port = 2001

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
clw = Claw(sock)
man = Servo(sock)
caught = False

def check(cords):
    global caught
    if cords[0]:
        start()
        move_to_target(0)
        lift()
        caught = True
    if cords[3] or cords[4]:
        if cords[3]:
            move_to_t(3)
        else:
            move_to_t(4)
    if cords[2]:
        move_to_t(2)
    else:
        return "STOP"
    


while True:
    man.basket_mode()
    clw.unclench()
    time.sleep(0.5)
    if check(send_coordinates()):
        break
    man.set(5, 0)
    time.sleep(0.5)
    if check(send_coordinates()):
        break
    man.set(5, 180)
    time.sleep(0.5)
    if check(send_coordinates()):
        break