from imageProcessing.detection import Detection
# from database.database import *
import cv2
from imageProcessing.misc import *
from hardware.camera import *


DEBUG = True


class Game:
    def __init__(self, website) -> None:
        self.score_red = 0
        self.score_blue = 0
        self.detector = Detection()
        self.mode = Mode.NORMAL
        self.website = website

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

    def run_camera(self, camera_id):
        camera = Camera(camera_id)
        while True:
            frame = camera.get_frame()
            if frame is None:
                print("frame none")
                frame = cv2.imread("Error_mirrored.jpg")
            frame = self.detector.run(frame, self.mode)
            if DEBUG: self.showFrame(frame)
            #encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    def add_goal(self, Left):
        "pass True if one goal should be added to the score of the left goal, else 1 will be added to the right goal"
        self.website.add_goal(Left)

#TOdo see if you can call de app.route('...') to referesh page or potentially
#referesh div box or in the websitre run function add it as file to watch


