from imageProcessing.detection import Detection
# from database.database import *
import cv2
from imageProcessing.misc import *

DEBUG = True


class Game:
    def __init__(self) -> None:
        self.score_red = 0
        self.score_blue = 0
        self.detector = Detection()
        self.mode = Mode.NORMAL
        # database = 

    def showFrame(self, frame):
        cv2.imshow('smol', frame)
        key = cv2.waitKey(1)
        if key:
            if key == ord('q'):
                exit(0)
            elif key == ord('r'):
                self.mode = Mode.RED
            elif key == ord('b'):
                self.mode = Mode.BLUE
            elif key == ord('f'):
                self.mode = Mode.FUNK
            elif key == ord('n'):
                self.mode = Mode.NORMAL
            elif key == ord('d'):
                self.mode = Mode.DISCO

    def kalmanFilter(self):
        pass

    def stream(self):
        pass

    def run(self):
        video = cv2.VideoCapture('data/video/shakiestcam.mp4')
        nextFrame = True
        while nextFrame:
            nextFrame, frame = video.read()
            if nextFrame == False:
                break
            frame = self.detector.run(frame, self.mode)
            
            if DEBUG: self.showFrame(frame)
        
        video.release()
        cv2.destroyAllWindows()