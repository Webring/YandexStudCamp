from ultralytics import YOLO
import cv2
import numpy as np
import logging
import time
from udis import udis

# 1960 x 1280
logging.getLogger('ultralytics').setLevel(logging.INFO)

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

capture = cv2.VideoCapture('ira.mp4')

# Чтение параметров видео
fps = int(capture.get(cv2.CAP_PROP_FPS))
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


frame_counter = 0  # Счетчик кадров

right_line = [1527, 49, 1635, 993]
left_line = [300, 76, 409, 1046]
up_line = np.zeros(4)
down_line = [420, 23, 1587, 94]

right_up_angle_hor = np.zeros(4)
right_up_angle_vert = np.zeros(4)
right_down_angle_hor = np.zeros(4)
right_down_angle_vert = np.zeros(4)
left_up_angle_hor = np.zeros(4)
left_up_angle_vert = np.zeros(4)
left_down_angle_hor = np.zeros(4)
left_down_angle_vert = np.zeros(4)

moving_wall_1 = np.zeros(4)
moving_wall_2 = np.zeros(4)


while True:
    # Захват кадра
    ret, frame = capture.read()
    if not ret:
        break

    # Обрабатываем каждый второй кадр
    if frame_counter % 1 == 0:
        # Обработка кадра с помощью модели YOLO
        #frame = udis(frame)
        results = model(frame)[0]

        # Получение данных об объектах
        classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

        center_x = 1960 * 0.6
        center_y = 1280 / 2

        
        for idx, label in enumerate(classes):
            box = boxes[idx]
            x1 = box[0]
            y1 = box[1]
            x2 = box[2]
            y2 = box[3]
            # ищем и определяем линии
            # TODO обработать случай когда задетектится лишняя левая/правая линия
            if label == 2:
                if x1 > center_x and y1 < center_y and x2 > center_x and y2 > center_y:
                    right_line = box
                elif x1 < center_x and y1 < center_y and x2 < center_x and y2 > center_y:
                    left_line = box
                elif x1 < center_x and y1 > center_y and x2 > center_x and y2 > center_y:
                    up_line = box
                elif x1 < center_x and y1 < center_y and x2 > center_x and y2 < center_y:
                    down_line = box

            # детектим уголки
            elif label == 0:
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
                if moving_wall_1[2] == 0:
                    moving_wall_1 = box
                else:
                    moving_wall_2 = box


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

        for pair in nodes:
            cv2.circle(frame, (int(pair[0]), int(pair[1])), 5, (0, 0, 255), -1)  # Красная точка, заполненная (-1)



        for class_id, box, conf in zip(classes, boxes, results.boxes.conf):
            if conf > 0.5:
                class_name = classes_names[int(class_id)]
                color = colors[int(class_id) % len(colors)]
                x1, y1, x2, y2 = box
 
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


    # Вывод обработанного кадра в окно (даже если он не был обработан моделью)
    cv2.imshow('YOLOv8 Live', frame)

    # Увеличиваем счетчик кадров
    frame_counter += 1

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    time.sleep(10)
# Освобождение ресурсов и закрытие окон
capture.release()
cv2.destroyAllWindows()
