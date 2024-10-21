from video_parser import send_coordinates
from socket import *
from control.libs.movement import Movement
from control.libs.manipulator import Claw, Servo
from control.libs.sensors import Sensors
from math import atan

host = "192.168.2.157"
port = 2001

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
sock.settimeout(2)
move = Movement(sock)
clw = Claw(sock)
man = Servo(sock)
sensors = Sensors(sock)

def move_to_basket():
    pass

def calculate_angle(claw, target):
    x_s, y_s = target
    x_e, y_e = claw
    return atan((max(x_s, x_e) - min(x_s, x_e)) / (max(y_s, y_e) - min(y_s, y_e)))