import cv2
from imageProcessing.detection import Detection
from random import choice

frame_count = 200
video = cv2.VideoCapture('./data/video/best yet.mp4')

refPt = []
cropping = False
global frame
skip_frames = 10
skip = False
detector = Detection(None)

def mouse_click(event, x, y, flags, param):
    global refPt, cropping, skip
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False
        cv2.rectangle(frame, refPt[0], refPt[1], (0, 255, 0), 2)
    elif event == cv2.EVENT_RBUTTONUP:
        skip = True

# Skip over frames
for i in range(0, frame_count):
    next, frame = video.read()
    cv2.rotate(frame, cv2.ROTATE_180, frame)
    detector.aruco(frame)
    # cv2.imshow('init', frame)
    # key = cv2.waitKey(100)
min_x, max_x, min_y, max_y = detector.min_x, detector.max_x, detector.min_y, detector.max_y
print(min_x, max_x, min_y, max_y)
frame = frame[min_y:max_y, min_x:max_x]
# cv2.imshow('init', frame)
# key = cv2.waitKey(10000)
# print(detector.min_x, detector.max_x, detector.min_y, detector.max_y)
# exit(0)
    
# cv2.setMouseCallback("image", mouse_click)

extra_count = 9000 - frame_count
for i in range(0, extra_count):
    next, frame = video.read()
    frame_count += 1
    if frame_count % 100 == 0:
        print(frame_count)

while True:
    for i in range(0, skip_frames):
        next, frame = video.read()
        frame_count += 1
    if not next: break
    cv2.rotate(frame, cv2.ROTATE_180, frame)
    frame = frame[min_y:max_y, min_x:max_x]
    # cv2.imshow('test', frame)
    # cv2.waitKey(100)
    cv2.imwrite(f'./datasets/custom/images/train/{frame_count}.jpg', frame)
    if frame_count % 50 == 0:
        print(f'Created images {frame_count-50}-{frame_count}')
    
    # clone = frame.copy()
    # while True:
    #     cv2.namedWindow("frame")
    #     cv2.setMouseCallback("frame", mouse_click)
    #     key = cv2.waitKey(1)
    #     if key == ord('q'):
    #         exit(0)
    #     elif key == ord("r"):
    #         frame = clone.copy()
    #     elif key == ord("s"):
    #          break
    #     elif key == ord("c") or key == 13 or skip:
    #         skip = False
    #         location = ['train', 'val']
    #         location = choice(location)
    #         with open(f'./datasets/custom/labels/{location}/{frame_count}.txt', 'w') as text_file:
    #             if len(refPt) == 2:
    #                 text_file.write(f'1, {refPt[0][0]} {refPt[0][1]} {refPt[1][0]} {refPt[1][1]}')
    #                 refPt = []
    #             else:
    #                 text_file.write(' ')
    #         cv2.imwrite(f'./datasets/custom/images/{location}/{frame_count}.jpg', clone)
    #         break
    #     cv2.imshow("frame", frame)

# video.release()
# cv2.destroyAllWindows()
