from backend.detection import Detection
import time
from collections import deque

from backend.misc import *
from hardware.camera import *
from env import *


class Game:
    def __init__(self, website) -> None:
        self.score_red = 0
        self.score_blue = 0
        self.detector = Detection(game=self)
        self.mode = Mode.NORMAL
        self.paused = False
        self.skip_frame = False
        self.time = 0
        self.back_frames = []
        self.front_frames = []
        self.max_back_frames = self.detector.fps
        self.video_frames = []
        self.video = None
        self.calibration_frames = 5
        self.website = website
        self.fps = 60
        self.delaysec = 5
        self.buffer = deque(maxlen=(self.fps * self.delaysec))

    def calibrate(self, video):
        nextFrame, frame = video.read()
        height, width, _ = frame.shape
        self.detector.setDimensions(frame)
        video.set(cv2.CAP_PROP_FRAME_WIDTH, int(width*1.3))  # Dimension of Iris' camera
        video.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))  # Dimension of Iris' camera
        for i in range(0, self.calibration_frames):
            nextFrame, frame = video.read()
            cv2.rotate(frame, cv2.ROTATE_180, frame)
            self.detector.aruco(frame)
        self.detector.calibrate(frame)

    def run(self, video):
        self.calibrate(video)
        video.set(cv2.CAP_PROP_FPS, 60)
        nextFrame = True
        frame = None
        while nextFrame:
            if self.paused and not self.skip_frame:
                return frame

            if self.skip_frame:
                self.skip_frame = False
            nextFrame, frame = self.getFrame(video)

            if DEBUG and False:
                frame = self.detector.run_debug(frame, self.mode)
            else:
                frame = self.detector.run(frame)

            self.showFrame(frame)

    def run_camera(self, video):
        self.calibrate(video)
        video.set(cv2.CAP_PROP_FPS, 60)
        while True:
            nextFrame, frame = self.getFrame(video)
            if not nextFrame:
                print("No frame")
                frame = cv2.imread("../website/Error_mirrored.jpg")
            frame = self.detector.run(frame)
            # Encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            self.buffer.append(jpeg)
            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    def getFrame(self, video):
        self.time += 1
        nextFrame, frame = video.read()
        if nextFrame:
            # frame = cv2.warpAffine(frame, self.detector.rotate_matrix, frame.shape[1::-1], flags=cv2.INTER_LINEAR)
            frame = frame[self.detector.min_y:self.detector.max_y, self.detector.min_x:self.detector.max_x]
        frame = self.detector.scale(frame, 1)
        return nextFrame, frame

    def buffer_frames(self):
        while True:
            bframes = self.buffer.copy()
            for jpeg in bframes:
                time.sleep(0.01)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    def add_goal(self, Left):
        "pass True if one goal should be added to the score of the left goal, else 1 will be added to the right goal"
        self.website.add_goal(Left)

    def showFrame(self, frame):
        """Show a frame in the backend, and detect any key presses to change the behaviour of the frame."""
        cv2.imshow('Foosball', frame)
        key = cv2.waitKey(1)
        match key:
            case 113:
                exit(69)
            case 114:
                self.mode = Mode.RED
            case 98:
                self.mode = Mode.BLUE
            case 102:
                self.mode = Mode.FUNK
            case 110:
                self.mode = Mode.NORMAL
            case 100:
                self.mode = Mode.DISCO
            case 111:
                self.mode = Mode.ORANGE
            case 115:
                self.detector.max_ball_speed = 0
            # case 99:
            #     self.detector.corners = [[]]*4
            #     self.calibrate()
            case 122:
                self.detector.zoom += 1
                if self.detector.zoom >= len(self.detector.zoom_levels):
                    self.detector.zoom = 0
            case 112:
                self.paused = not self.paused
            case 61:
                self.skip_frames = 1
        return


#TOdo see if you can call de app.route('...') to referesh page or potentially
#referesh div box or in the websitre run function add it as file to watch
