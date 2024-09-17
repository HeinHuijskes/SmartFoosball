import cv2

def detect():
    video = cv2.VideoCapture('data/video/IMG_6903.MOV')

    nextFrame = True
    framecounter = 0
    while nextFrame:
        nextFrame, frame = video.read()
        if framecounter < 1000:
            framecounter += 1
            continue
        cv2.imshow('colour', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()