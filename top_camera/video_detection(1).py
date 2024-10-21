from ultralytics import YOLO
import cv2
import numpy as np
from udis import udis
import math
# Загрузка модели YOLOv8
model = YOLO('best_top_camera.pt')
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
# Список цветов для различных классов
colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
    (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
    (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
]

capture = cv2.VideoCapture("top_camera_video.mp4")

# Чтение параметров видео
fps = int(capture.get(cv2.CAP_PROP_FPS))
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


frame_counter = 0  # Счетчик кадров

while True:
    # Захват кадра
    ret, frame = capture.read()
    if not ret:
        break

    # Обрабатываем каждый второй кадр
    if frame_counter % 1 == 0:
        # Обработка кадра с помощью модели YOLO
        #frame = udis(frame)0]
        frame = cv2.resize(frame, (1920, 1280))
        results = model(frame, verbose=False)[0]

        # Получение данных об объектах
        classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)
        x_mean_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6:[], 7:[], 8:[]}
        for class_id, box, conf in zip(classes, boxes, results.boxes.conf):
            if conf > 0.55:
                class_name = classes_names[int(class_id)]
                color = colors[int(class_id) % len(colors)]
                x1, y1, x2, y2 = box
                x_mean = int(np.mean([x1, x2]))
                y_mean = int(np.mean([y1, y2]))
                x_mean_dict[int(class_id)].append((x_mean, y_mean))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.line(frame, x_mean_dict[3][-1], (0, 0), (255, 0 ,0), 3)
        cv2.line(frame, x_mean_dict[3][-1], x_mean_dict[2][-2], (255, 0, 0), 3)
        # cv2.circle(frame, (1511, 548), 5, (255, 0 ,0), -1)
        # print(calculate_angle(x_mean_dict[4][-1], x_mean_dict[2][-1], (1511, 548)))
        # print(x_mean_dict)
        '''if len(x_mean_dict[5]) * len(x_mean_dict[3]) != 0:
            start_point = x_mean_dict[5][-1]
            end_point = x_mean_dict[3][-1]
            x_e, _ = x_mean_dict[5][-1]
            _, y_e = x_mean_dict[3][-1]
            end_point_2 = (x_e, y_e)
            cv2.line(frame, start_point, end_point, color=(255, 255, 255), thickness=2)
            cv2.line(frame, start_point, end_point_2, color=(255, 255, 255), thickness=2)
            x_s, y_s = x_mean_dict[5][-1]
            x_e, y_e = x_mean_dict[3][-1]
            print(-np.arctan((x_s - x_e) / (0.00001 + y_s - y_e)))'''

    # Вывод обработанного кадра в окно (даже если он не был обработан моделью)
        cv2.imshow('YOLOv8 Live', cv2.resize(frame, (1080, 1080)))
    input()
    # Увеличиваем счетчик кадров
    frame_counter += 1

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождение ресурсов и закрытие окон
capture.release()
cv2.destroyAllWindows()