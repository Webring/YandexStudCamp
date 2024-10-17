from os import system
from ultralytics import YOLO
import cv2
import numpy as np

def send_coordinates():
    model = YOLO('best.pt')

# Список цветов для различных классов
    colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
    (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
    (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
    ]

    capture = cv2.VideoCapture("http://192.168.2.157:8081/")

# Чтение параметров видео
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_counter = 0  # Счетчик кадров

    mean_dict = {0: [], 1: [], 2: [], 3:[], 4:[], 5: []}
    for i in range(8):
    # Захват кадра
        ret, frame = capture.read()
        if not ret:
            break
        # Обрабатываем каждый второй кадр
        # Обработка кадра с помощью модели YOLO
        results = model(frame)[0]

        # Получение данных об объектах
        classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)


        # Рисование рамок и подписей на кадре
        for class_id, box, conf in zip(classes, boxes, results.boxes.conf):
            if conf > 0.45:
                class_name = classes_names[int(class_id)]
                color = colors[int(class_id) % len(colors)]
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                print(int(class_id))
                mean_dict[int(class_id)].append((np.mean([x1, x2]), np.mean([y1, y2])))
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


# Освобождение ресурсов и закрытие окон
    capture.release()
    cv2.destroyAllWindows()
    final_dict = {}
    for key, value in mean_dict.items():
        if len(value) == 0:
            continue
        x_mean = []
        y_mean = []
        for point in value:
            x, y = point
            x_mean.append(x)
            y_mean.append(y) 
        final_dict[key] = (int(np.mean(x_mean)), int(np.mean(y_mean)))
    return final_dict
