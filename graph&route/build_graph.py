from ultralytics import YOLO
import cv2
import numpy as np
import logging
from udis import udis
import math


robot_label = 4  # 3 - зеленый, 4 - красный
base_label = robot_label + 3

def calculate_angle(point_a, point_b, point_c):
    x1, y1 = point_a
    x2, y2 = point_b
    x3, y3 = point_c

    AB = (x2 - x1, y2 - y1)
    AC = (x3 - x1, y3 - y1)

    dot_product = AB[0] * AC[0] + AB[1] * AC[1]

    AB_length = math.sqrt(AB[0]**2 + AB[1]**2)
    AC_length = math.sqrt(AC[0]**2 + AC[1]**2)

    cos_alpha = dot_product / (AB_length * AC_length)

    alpha = math.acos(cos_alpha)

    if (x3 - x1)*(y2 - y1) - (y3 - y1)*(x2 - x1) > 0:
        return alpha
    else:
        return -alpha
    


def graph():
    # Загрузка модели YOLOv8
    model = YOLO('best_top_camera.pt')
    ip_camera_url_left = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
    # Список цветов для различных классов
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
        (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
        (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
        (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
    ]

    capture = cv2.VideoCapture(ip_camera_url_left)

    # Чтение параметров видео
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 1960 x 1280
    logging.getLogger('ultralytics').setLevel(logging.INFO)


    '''# TODO задать значения по умолчанию
    right_line = [1527, 49, 1635, 993]
    left_line = [300, 76, 409, 1046]
    up_line = np.zeros(4)
    down_line = [420, 23, 1587, 94]'''

    right_up_angle_hor = [1066, 864, 1264, 931]
    right_up_angle_vert = [1225, 663, 1260, 935]
    right_down_angle_hor = [1071, 172, 1289, 244]
    right_down_angle_vert = [1226, 182, 1277, 454]
    left_up_angle_hor = [673, 153, 869, 227]
    left_up_angle_vert = [665, 154, 712, 431]
    left_down_angle_hor = [658, 856, 849, 918]
    left_down_angle_vert = [653, 652, 695, 913]

    moving_wall_right = np.zeros(4)
    moving_wall_left = np.zeros(4)
    moving_wall_up = np.zeros(4)
    moving_wall_down = np.zeros(4)

    robot_center = [0, 0]

    cubes = [[0, 0], [0, 0]]
    cubes_number = 0

    base_center = [0, 0]


    center_x = width / 2
    center_y = height / 2
    #print(center_x, center_y)

    # Захват кадра
    ret, frame = capture.read()
    if not ret:
        return
    #frame = udis(frame)
    # Обрабатываем каждый второй кадр

    # Обработка кадра с помощью модели YOLO
    frame = udis(frame)
    frame = frame[:, 400:1600]
    frame = cv2.resize(frame, (1920, 1080))
    results = model(frame)[0]

    # Получение данных об объектах
    classes_names = results.names
    classes = results.boxes.cls.cpu().numpy()
    boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

    
    for label, box, conf in zip(classes, boxes, results.boxes.conf):
        print(label, box)
        if conf > 0.5:
            x1, y1, x2, y2 = box
            # ищем и определяем линии
            # TODO обработать случай когда задетектится лишняя левая/правая линия
            '''if label == 2:
                if x1 > center_x and y1 < center_y and x2 > center_x and y2 > center_y:
                    right_line = box
                elif x1 < center_x and y1 < center_y and x2 < center_x and y2 > center_y:
                    left_line = box
                elif x1 < center_x and y1 > center_y and x2 > center_x and y2 > center_y:
                    up_line = box
                elif x1 < center_x and y1 < center_y and x2 > center_x and y2 < center_y:
                    down_line = box'''

            # детектим уголки
            if label == 0:
                if x1 > center_x and y1 > center_y and x2 > center_x and y2 > center_y:
                    if x2 - x1 > y2 - y1:
                        right_up_angle_hor = box
                    else:
                        right_up_angle_vert = box
                elif x1 > center_x and y1 < center_y and x2 > center_x and y2 < center_y:
                    if x2 - x1 > y2 - y1:
                        right_down_angle_hor = box
                    else:
                        right_down_angle_vert = box
                elif x1 < center_x and y1 < center_y and x2 < center_x and y2 < center_y:
                    if x2 - x1 > y2 - y1:
                        left_down_angle_hor = box
                    else:
                        left_down_angle_vert = box
                elif x1 < center_x and y1 > center_y and x2 < center_x and y2 > center_y:
                    if x2 - x1 > y2 - y1:
                        left_up_angle_hor = box
                    else:
                        left_up_angle_vert = box

            # детектим передвижные перегородки
            elif label == 1:
                if x1 > center_x and y1 < center_y and x2 > center_x and y2 > center_y:
                    moving_wall_right = box
                elif x1 < center_x and y1 < center_y and x2 < center_x and y2 > center_y:
                    moving_wall_left = box
                elif x1 < center_x and y1 > center_y and x2 > center_x and y2 > center_y:
                    moving_wall_up = box
                elif x1 < center_x and y1 < center_y and x2 > center_x and y2 < center_y:
                    moving_wall_down = box

            # детектим робота
            elif label == robot_label:
                robot_center = [0.5 * (x1 + x2), 0.5 * (y1 + y2)]

            # детектим кубики
            elif label == 8:
                if cubes_number < 2:
                    cubes[cubes_number] = [0.5 * (x1 + x2), 0.5 * (y1 + y2)]
                    cubes_number += 1

            # детектим базу
            elif label == base_label:
                base_center = [0.5 * (x1 + x2), 0.5 * (y1 + y2)]
    

    #print()
    # строим опорные точки
    nodes = []

    # внутри уголков
    right_up_x = 0.5 * (right_up_angle_hor[0] + right_up_angle_vert[0])
    right_up_y = 0.5 * (right_up_angle_hor[1] + right_up_angle_vert[1])
    nodes.append([right_up_x, right_up_y])  # 1

    right_down_x = 0.5 * (right_down_angle_hor[0] + right_down_angle_vert[0])
    right_down_y = 0.5 * (right_down_angle_hor[3] + right_down_angle_vert[3])
    nodes.append([right_down_x, right_down_y])  # 2

    left_down_x = 0.5 * (left_down_angle_hor[2] + left_down_angle_vert[2])
    left_down_y = 0.5 * (left_down_angle_hor[3] + left_down_angle_vert[3])
    nodes.append([left_down_x, left_down_y])  # 3

    left_up_x = 0.5 * (left_up_angle_hor[2] + left_up_angle_vert[2])
    left_up_y = 0.5 * (left_up_angle_hor[1] + left_up_angle_vert[1])
    nodes.append([left_up_x, left_up_y])  # 4

    # внутренний контур, но не уголки
    nodes.append([0.5 * (right_up_x + right_down_x), 0.5 * (right_up_y + right_down_y)])  # 5
    nodes.append([0.5 * (left_down_x + right_down_x), 0.5 * (left_down_y + right_down_y)])  # 6
    nodes.append([0.5 * (left_down_x + left_up_x), 0.5 * (left_down_y + left_up_y)])  # 7
    nodes.append([0.5 * (right_up_x + left_up_x), 0.5 * (right_up_y + left_up_y)])  # 8

    # внешний контур, серединки
    right_center_x = 0.25 * (right_up_angle_vert[0] + right_up_angle_vert[2] + right_down_angle_vert[0] + right_down_angle_vert[2])
    nodes.append([2 * right_center_x - nodes[4][0], nodes[4][1]])  # 9

    down_center_y = 0.25 * (right_down_angle_hor[1] + right_down_angle_hor[3] + left_down_angle_hor[1] + left_down_angle_hor[3])
    nodes.append([nodes[5][0], 1.5 * down_center_y - 0.5 * nodes[5][1]])  # 10

    left_center_x = 0.25 * (left_up_angle_vert[0] + left_up_angle_vert[2] + left_down_angle_vert[0] + left_down_angle_vert[2])
    nodes.append([2 * left_center_x - nodes[6][0], nodes[6][1]])  # 11

    up_center_y = 0.25 * (right_up_angle_hor[1] + right_up_angle_hor[3] + left_up_angle_hor[1] + left_up_angle_hor[3])
    nodes.append([nodes[7][0], 1.5 * up_center_y - 0.5 * nodes[7][1]])  # 12

    # внешние углы
    nodes.append([nodes[8][0], nodes[11][1]])  # 13
    nodes.append([nodes[8][0], nodes[9][1]])  # 14
    nodes.append([nodes[10][0], nodes[9][1]])  # 15
    nodes.append([nodes[10][0], nodes[11][1]])  # 16


    # добавляем ребра
    edges = np.zeros((16, 16))
    edges[0][4] = edges[4][0] = 1
    edges[0][7] = edges[7][0] = 1
    edges[1][4] = edges[4][1] = 1
    edges[1][5] = edges[5][1] = 1
    edges[2][5] = edges[5][2] = 1
    edges[2][6] = edges[6][2] = 1
    edges[6][3] = edges[3][6] = 1
    edges[3][7] = edges[7][3] = 1

    edges[10][15] = edges[15][10] = 1
    edges[10][14] = edges[14][10] = 1
    edges[11][15] = edges[15][11] = 1
    edges[9][14] = edges[14][9] = 1
    edges[11][12] = edges[12][11] = 1
    edges[9][13] = edges[13][9] = 1
    edges[8][12] = edges[12][8] = 1
    edges[8][13] = edges[13][8] = 1

    if moving_wall_right[0] == 0:
        edges[8][4] = edges[4][8] = 1
    if moving_wall_left[0] == 0:
        edges[6][10] = edges[10][6] = 1
    if moving_wall_down[0] == 0:
        edges[9][5] = edges[5][9] = 1
    if moving_wall_up[0] == 0:
        edges[7][11] = edges[11][7] = 1


    '''
    print(right_up_angle_hor)
    print(right_up_angle_vert)
    print(right_down_angle_hor)
    print(right_down_angle_vert)
    print(left_down_angle_hor)
    print(left_down_angle_vert)
    print(left_up_angle_hor)
    print(left_up_angle_vert)
    print(f"y: {center_y}")
    '''
    #cv2.circle(frame, (int(center_x), int(center_y)), 5, (255, 0, 0), -1)
    
    '''
    print(right_line)
    print(left_line)
    print(up_line)
    print(down_line)
    '''
    '''
    print(moving_wall_right)
    print(moving_wall_left)
    print(moving_wall_up)
    print(moving_wall_down)
    '''

    '''for i, pair in enumerate(nodes):
        cv2.circle(frame, (int(pair[0]), int(pair[1])), 5, (0, 0, 255), -1)  # Красная точка, заполненная (-1)
        #print(pair)
        #if i == 8:
            #print(pair)
        for j, pair_2 in enumerate(nodes):
            if i != j and edges[i][j] == 1:
                x1, y1 = int(pair[0]), int(pair[1])
                x2, y2 = int(pair_2[0]), int(pair_2[1])
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)'''





    '''for class_id, box, conf in zip(classes, boxes, results.boxes.conf):
        if conf > 0.5:
            class_name = classes_names[int(class_id)]
            color = colors[int(class_id) % len(colors)]
            x1, y1, x2, y2 = box
            #if class_id == 3:
            #    x_mean = np.mean(x1, x2)
            if class_id == 4:
                robot_center_x, robot_center_y = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                cv2.circle(frame, (int(robot_center_x), int(robot_center_y)), 5, (0, 255, 0), -1)

            if class_id == 2:
                claw_center_x, claw_center_y = 0.5 * (x1 + x2), 0.5 * (y1 + y2)

        
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        print(robot_center_x, robot_center_y)
        print(claw_center_x, claw_center_y)
        cv2.line(frame, (int(robot_center_x), int(robot_center_y)), (int(1475.75), int(555.75)), (0, 255, 0), 3)
        cv2.line(frame, (int(robot_center_x), int(robot_center_y)), (int(claw_center_x), int(claw_center_y)), (255, 255, 0), 3)
        print(calculate_angle([robot_center_x, robot_center_y], [claw_center_x, claw_center_y], [1475.75, 555.75]))

        # Вывод обработанного кадра в окно (даже если он не был обработан моделью)
        cv2.circle(frame, (1476, 556), 5, (0, 0, 255), -1)  # Красная точка, заполненная (-1)
        cv2.imshow('YOLOv8 Live', frame)

        # Увеличиваем счетчик кадров
        frame_counter += 1
        capture.release()
        cv2.destroyAllWindows()'''
    
    return nodes, edges, robot_center, base_center, cubes_number, cubes