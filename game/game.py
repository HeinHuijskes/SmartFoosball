from hardware.arduino import Arduino, Team
from colorama import Fore, Back, Style
from imageProcessing.detection import Detection
# from database.database import *
import cv2
from imageProcessing.misc import *
from hardware.camera import *

DEBUG = True


class Game:
    def __init__(self) -> None:
        self.score_red = 0
        self.score_blue = 0
        self.detector = Detection()
        self.mode = Mode.NORMAL
        self.arduino = Arduino()
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
            elif key == ord('o'):
                self.mode = Mode.ORANGE

    def kalmanFilter(self):
        pass

    def stream(self):
        pass

    def run(self):
        video = cv2.VideoCapture('data/video/tafelvoetbal_oranjebal.mp4')
        nextFrame = True
        while nextFrame:
            nextFrame, frame = video.read()
            if nextFrame == False:
                break
            frame = self.detector.run(frame, self.mode)
            self.check_goal()

            if DEBUG: self.showFrame(frame)

        video.release()
        cv2.destroyAllWindows()

    def run_website(self, video_feed):
        nextFrame = True
        while nextFrame:
            nextFrame, frame = video_feed.read()
            if not nextFrame:
                break
            frame = self.detector.run(frame, self.mode)
            # cv2.imshow('test', frame)
            self.showFrame(frame)
            # encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            if frame is None or frame.size == 0:
                print("frame error")
            if ret:
                self.check_goal()

                frame = jpeg.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       frame + b'\r\n')

    def check_goal(self):
        goal_team = self.arduino.get_goal()
        if goal_team == Team.BLUE:
            self.score_blue += 1
            print(Fore.BLUE, "blue:", self.score_blue, Fore.RED, "red:", self.score_red, Style.RESET_ALL)
        elif goal_team == Team.RED:
            self.score_red += 1
            print(Fore.BLUE, "blue:", self.score_blue, Fore.RED, "red:", self.score_red, Style.RESET_ALL)