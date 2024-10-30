import cv2
from backend.detection import Detection

calibration_frames = 10
video = cv2.VideoCapture('./data/video/bordeelvoetbal.mp4')

refPt = []
cropping = False
skip_frames = 10
skip = False
detector = Detection(None)

# Skip over frames
nextFrame, frame = video.read()
height, width, _ = frame.shape
width = width * 1.3
video.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
video.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
while not detector.calibrated:
    print("Calibrating")
    for i in range(0, calibration_frames):
        nextFrame, frame = video.read()
        detector.aruco(frame)
    detector.calibrate(frame)

counter = 0
while nextFrame:
    print(f'At frame {counter}')
    nextFrame, frame = video.read()
    frame = cv2.warpAffine(frame, detector.rotate_matrix, frame.shape[1::-1])
    frame = frame[detector.min_y:detector.max_y, detector.min_x:detector.max_x]
    if counter % skip_frames == 0:
        number = "{:05d}".format(counter)
        cv2.imwrite(f'./datasets/white/{number}.jpg', frame)
    cv2.imshow('Shitfuck', frame)
    key = cv2.waitKey(1)
    counter += 1


cv2.destroyAllWindows()
