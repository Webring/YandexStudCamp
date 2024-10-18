from ultralytics import YOLO
import cv2
import numpy as np
import logging
logging.getLogger('ultralytics').setLevel(logging.INFO)
# Загрузка модели YOLOv8
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

while True:
    # Захват кадра
    ret, frame = capture.read()
    if not ret:
        break

    # Обрабатываем каждый второй кадр
    if frame_counter % 3 == 0:
        # Обработка кадра с помощью модели YOLO
        results = model(frame, verbose=False)[0]

        # Получение данных об объектах
        classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)
        x_mean_dict = {0: [], 1: [], 5: [], 2: [], 4: [], 3: []}
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
        print(x_mean_dict)
        if len(x_mean_dict[5]) * len(x_mean_dict[0]) != 0:
            start_point = x_mean_dict[5][-1]
            end_point = x_mean_dict[0][-1]
            x_e, _ = x_mean_dict[5][-1]
            _, y_e = x_mean_dict[0][-1]
            end_point_2 = (x_e, y_e)
            cv2.line(frame, start_point, end_point, color=(255, 255, 255), thickness=2)
            cv2.line(frame, start_point, end_point_2, color=(255, 255, 255), thickness=2)
            x_s, y_s = x_mean_dict[5][-1]
            x_e, y_e = x_mean_dict[0][-1]
            print(np.arctan((x_s - x_e) / (0.00001 + y_s - y_e)))

    # Вывод обработанного кадра в окно (даже если он не был обработан моделью)
    cv2.imshow('YOLOv8 Live', cv2.resize(frame, (720, 720)))

    # Увеличиваем счетчик кадров
    frame_counter += 1

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождение ресурсов и закрытие окон
capture.release()
cv2.destroyAllWindows()