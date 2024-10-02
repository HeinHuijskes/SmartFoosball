from ultralytics import YOLO
import cv2
import math
from imageProcessing.detection import Detection

model = YOLO("./runs/detect/train19/weights/best.pt")
video = cv2.VideoCapture('data/video/quite long.mp4')
detector = Detection(None)
frame_count = 200

classNames = ["balls"]

for i in range(0, frame_count):
    next_frame, frame = video.read()
    # cv2.rotate(frame, cv2.ROTATE_180, frame)
    detector.aruco(frame)
min_x, max_x, min_y, max_y = detector.min_x, detector.max_x, detector.min_y, detector.max_y
print(min_x, max_x, min_y, max_y)

for i in range(0, 500):
    next_frame, frame = video.read()
    if not next_frame:
        break

while True:
    next_frame, frame = video.read()
    if not next_frame:
        break
    # cv2.rotate(frame, cv2.ROTATE_180, frame)
    frame = frame[min_y:max_y, min_x:max_x]

    results = model(frame)
    # print(results)
    for r in results:
        boxes = r.boxes
        # print(boxes)
        for box in boxes:
            print(box)
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 0, 255), 2)

            conf = math.ceil((box.conf[0] * 100)) / 100

            cls = box.cls[0]
            name = classNames[int(cls)]
            cv2.putText(frame, f'{name} {conf}', (max(0, x1), max(35, y1)), 1, 1, (0, 0, 255), 2, cv2.LINE_AA)

    while True:
        cv2.imshow('image', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break