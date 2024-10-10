from imageProcessing.detection import Detection
import time
from collections import deque

# from database.database import *
import cv2
from imageProcessing.misc import *
from hardware.camera import *

DEBUG = True


class Game:
    def __init__(self, website) -> None:
        self.score_red = 0
        self.score_blue = 0
        self.detector = Detection(game=self)
        self.mode = Mode.NORMAL
        self.paused = False
        self.skip_frames = 0
        self.skip_range = [ord(f'{x}') for x in range(1, 10)]
        self.time = 0
        self.back_frames = []
        self.front_frames = []
        self.max_back_frames = self.detector.fps
        self.video_frames = []
        self.calibration_frames = 5
        self.website = website
        self.fps = 60
        self.delaysec = 5
        self.buffer = deque(maxlen=(self.fps * self.delaysec))
        self.max_speed = [1]
        self.camera = None


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
            elif key == ord('s'):
                self.detector.max_ball_speed = 0
            # elif key == ord('c'):
            #     self.detector.corners = [[]]*4
            #     self.calibrate()
            elif key == ord('z'):
                self.detector.zoom += 1
                if self.detector.zoom >= len(self.detector.zoom_levels):
                    self.detector.zoom = 0
            elif key == ord('p'):
                self.paused = not self.paused
            elif self.paused:
                if key in self.skip_range:
                    self.skip_frames = self.detector.fps//3*int(chr(key))
                elif key == ord('='):
                    self.skip_frames = 1
                # elif key == ord('-'):
                #     self.skip_frames = -1

    def stream(self):
        pass

    def calibrate(self):
        nextFrame, frame = self.video.read()
        height, width, _ = frame.shape
        self.detector.setDimensions(frame)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, int(width*1.3))  # Dimension of Iris' camera
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))  # Dimension of Iris' camera
        for i in range(0, self.calibration_frames):
            nextFrame, frame = self.video.read()
            cv2.rotate(frame, cv2.ROTATE_180, frame)
            self.detector.aruco(frame)
        self.detector.calibrate(frame)

    def run(self):
        while True:
            self.video = cv2.VideoCapture('data/video/best yet.mp4')
            # self.video = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            self.calibrate()
            nextFrame = True
            while nextFrame:
                if not self.paused:
                    nextFrame, frame = self.getFrame()
                    if DEBUG:
                        frame = self.detector.run_debug(frame, self.mode)
                    else:
                        frame = self.detector.run(frame)

                elif self.skip_frames > 0:
                    for i in range(0, self.skip_frames):
                        nextFrame, frame = self.getFrame()
                        if not nextFrame:
                            break
                        if DEBUG:
                            frame = self.detector.run_debug(frame, self.mode)
                        else:
                            frame = self.detector.run(frame)
                    self.skip_frames = 0

                else:
                    # Paused and mode change, only show the change
                    self.showFrame(self.detector.applyMode(self.mode, frame))
                    continue

                if not nextFrame:
                    break
                self.showFrame(frame)

    def getFrame(self):
        self.time += 1
        nextFrame, frame = self.video.read()
        if nextFrame:
            # frame = cv2.warpAffine(frame, self.detector.rotate_matrix, frame.shape[1::-1], flags=cv2.INTER_LINEAR)
            frame = frame[self.detector.min_y:self.detector.max_y, self.detector.min_x:self.detector.max_x]
        frame = self.detector.scale(frame, 1)
        return nextFrame, frame

    def run_website(self, video_feed):
        nextFrame = True
        while nextFrame:
            nextFrame, frame = video_feed.read()
            if not nextFrame:
                break
            frame = self.detector.run_debug(frame, self.mode)
            # cv2.imshow('test', frame)
            self.showFrame(frame)
            # encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            if frame is None or frame.size == 0:
                print("frame error")
            if ret:
                frame = jpeg.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       frame + b'\r\n')

    def run_camera(self, camera):
        self.camera = camera
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                print("frame none")
                frame = cv2.imread("website/Error_mirrored.jpg")
            frame, max_speed = self.detector.run(frame)  # self.mode
            if DEBUG: self.showFrame(frame)
            #encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            self.buffer.append(jpeg)
            if ret:

                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')
                self.max_speed.append(max_speed)
    def buffer_frames(self):
            bframes = self.buffer.copy()
            for jpeg in bframes:
                time.sleep(0.01)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    def add_goal(self, Red):
        "pass True if one goal should be added to the score of the left goal (RED), else 1 will be added to the right goal (BLUE)"
        self.website.add_goal(Red)

    def get_max_speed(self):
        maxspd = self.max_speed
        self.max_speed = [maxspd[0]]
        return sum(maxspd)/ len(maxspd)

    def reset_max_speed(self):
        self.max_speed = [0]
    def reset_game(self):
        self.score_red = 0
        self.score_blue = 0
#         maybe also reset max speed

#TOdo see if you can call de app.route('...') to referesh page or potentially
#referesh div box or in the websitre run function add it as file to watch
