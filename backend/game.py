import time

import cv2

from backend.detection import Detection
from backend.gameSettings import GameSettings
from backend.misc import *
# from hardware.camera import *
from env import *
from hardware.mqtt_connection import Mqttserver, Team


class Game(GameSettings):
    def __init__(self, website) -> None:
        super().__init__()
        self.detector = Detection(game=self)
        self.website = website
        self.score_red = 0
        self.score_blue = 0


    def calibrate(self, setup=False):
        """Calibrates with aruco codes. Calibrates for a set amount of frames, defined in `self.calibration_frames`."""
        nextFrame, frame = self.video.read()

        if setup:
            # Scale up the width slightly to be able to detect aruco codes.
            # Don't scale up too much, since that severely impacts performance
            height, width, _ = frame.shape
            width = width*1.3
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))

        # Find the aruco codes over multiple frames.
        # `Detection.aruco()` automatically sets the detected table size after a certain amount of frames.
        for i in range(0, self.calibration_frames):
            nextFrame, frame = self.video.read()
            self.detector.aruco(frame)
            self.showFrame(frame)
        self.detector.calibrate(frame)

    def run(self, video):
        """Runs a game locally"""
        self.video = video
        self.calibrate(setup=True)
        # Set to video input FPS
        self.video.set(cv2.CAP_PROP_FPS, 60)
        nextFrame = True
        frame = None
        while nextFrame:
            if self.paused and not self.skip_frame:
                self.showFrame(frame)
                continue

            if self.skip_frame:
                self.skip_frame = False
            nextFrame, frame = self.getFrame(video)

            if DEBUG:
                frame = self.detector.detect_debug(frame, self.mode)
            else:
                frame = self.detector.detect(frame)

            self.showFrame(frame)

    def run_website(self, video):
        """Runs a game for website use, yielding encoded frames"""
        self.video = video
        self.calibrate(setup=True)
        # Set to input feed FPS
        end = time.time()
        start = time.time()
        while True:
            frame_time = end - start
            start = time.time()
            nextFrame, frame = self.getFrame(video)
            # Send error image in case video feed does not work
            if not nextFrame:
                print("No frame")
                frame = cv2.imread("../website/Error_mirrored.jpg")
            frame = self.detector.detect(frame)
            # Encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            self.buffer.append((jpeg, frame_time))
            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

                self.average_speed.append(average_ball_speed)
                self.max_speed.append(self.detector.max_ball_speed)
            end = time.time()

    def getFrame(self, video):
        """Reads a frame from the video input and cuts it to the correct size"""
        self.time += 1
        nextFrame, frame = video.read()
        if nextFrame and self.detector.calibrated:
            frame = cv2.warpAffine(frame, self.detector.rotate_matrix, frame.shape[1::-1])
            frame = frame[self.detector.min_y:self.detector.max_y, self.detector.min_x:self.detector.max_x]
        return nextFrame, frame

    def buffer_frames(self):
        while True:
            bframes = self.buffer.copy()
            for jpeg in bframes:
                time.sleep(0.01)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    # def add_goal(self, Left):
    #     """pass True if one goal should be added to the score of the left goal,
    #     else 1 will be added to the right goal"""
    #     self.website.add_goal(Left)

    def showFrame(self, frame):
        """Show a frame in the backend, and detect any key presses to change the behaviour of the frame."""
        cv2.imshow('Foosball', frame)
        key = cv2.waitKey(1)
        match key:
            case 113:  # pressed 'q'
                exit('YOU EXITED?!')
            case 114:  # pressed 'r'
                self.mode = Mode.RED
            case 98:  # pressed 'b'
                self.mode = Mode.BLUE
            case 102:  # pressed 'f'
                self.mode = Mode.FUNK
            case 110:  # pressed 'n'
                self.mode = Mode.NORMAL
            case 100:  # pressed 'd'
                self.mode = Mode.DISCO
            case 115:  # pressed 's'
                self.detector.max_ball_speed = 0
            case 99:  # pressed 'c'
                self.detector.corners = [[], [], [], []]
                self.calibrate()
            case 122:  # pressed 'z'
                self.detector.zoom += 1
                if self.detector.zoom >= len(self.detector.zoom_levels):
                    self.detector.zoom = 0
            case 112:  # pressed 'p'
                self.paused = not self.paused
            case 61:  # pressed '='
                self.skip_frames = 1
        return

    def buffer_frames(self):
        time.sleep(3)
        if len(self.buffer) == self.buffer_max_len:
            bframes = self.buffer.copy()
            self.buffer.clear()
            for jpeg, frame_time in bframes:
                # if len(self.buffer) != 0:
                #         jpeg, frame_time = self.buffer.popleft()
                # self.showFrame(jpeg)
                # print(frame_time, "frame_time")
                if frame_time > 0:
                    time.sleep(2 * frame_time)
                    # print(jpeg)
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                           jpeg.tobytes() + b'\r\n')
                else:
                    continue
        while True:
            # print("hello")
            for i in range(self.buffer_max_len//2):
                if len(self.buffer) !=0:
                    # bframes = self.buffer.copy()
                    # self.buffer.clear()
                    # for jpeg, frame_time in bframes:
                # if len(self.buffer) != 0:
                        jpeg, frame_time = self.buffer.popleft()
                        # self.showFrame(jpeg)
                        # print(frame_time, "frame_time")
                        if frame_time > 0 :
                            time.sleep(frame_time)
                            # print(jpeg)
                            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                               jpeg.tobytes() + b'\r\n')
                        else: continue

    def add_goal(self, team, score):
        "pass True if one goal should be added to the score of the left goal (RED), else 1 will be added to the right goal (BLUE)"
        if team == Team.RED:
            self.score_red = score
        else:
            self.score_blue = score

    def get_max_speed(self):
        maxspd = self.max_speed
        self.max_speed = [maxspd[0]]
        return sum(maxspd)/ len(maxspd)

    def reset_max_speed(self):
        self.max_speed = [0]


    def get_average_speed(self):
        spd = self.average_speed
        self.average_speed = [spd[-1]]
        print("spd: ", spd, "average_spd", self.average_speed)
        return sum(spd)/ len(spd)

    def reset_max_speed(self):
        self.average_speed = [0]

    def reset_game(self):
        self.score_red = 0
        self.score_blue = 0
#         maybe also reset max speed
