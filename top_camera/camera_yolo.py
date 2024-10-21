from ultralytics import YOLO
import cv2
import numpy as np
import logging

from udis import udis

def distanse(point_a, point_b):
    x_a, y_a = point_a
    x_b, y_b = point_b
    return np.sqrt((x_a - x_b)**2 + (y_a - y_b)**2)

frame_counter = 0  # Счетчик кадров
logging.getLogger('ultralytics').setLevel(logging.INFO)

ip_camera_url_left = "top_camera_video.mp4"  # URL для подключения к IP-камере. Это может быть RTSP или другой протокол потокового видеоip_camera_url_left = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
# Загрузка модели YOLOv8
model = YOLO('best_top_camera.pt')

# Список цветов для различных классов
colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
    (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
    (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
]

capture = cv2.VideoCapture(ip_camera_url_left)
def state():
    global frame_counter
    ret, frame = capture.read()
    if not ret:
        return
    x_mean_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
    frame = cv2.resize(frame, (1920, 1080))

    results = model(frame, show=True, verbose=False)[0]
    classes = results.boxes.cls.cpu().numpy()
    boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

    for class_id, box, conf in zip(classes, boxes, results.boxes.conf):
        if conf > 0.50:
            x1, y1, x2, y2 = box
            color = colors[int(class_id) % len(colors)]
            x_mean = int(np.mean([x1, x2]))
            y_mean = int(np.mean([y1, y2]))
            x_mean_dict[int(class_id)].append((x_mean, y_mean)) 
    return x_mean_dict

