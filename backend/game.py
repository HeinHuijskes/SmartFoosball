import time

import cv2

from backend.detection import Detection
from backend.gameSettings import GameSettings
from backend.misc import *
from hardware.camera import *
from env import *


class Game(GameSettings):
    def __init__(self, website) -> None:
        super().__init__()
        self.detector = Detection(game=self)
        self.website = website

    def calibrate(self):
        """Calibrates with aruco codes. Calibrates for a set amount of frames, defined in `self.calibration_frames`."""
        nextFrame, frame = self.video.read()
        height, width, _ = frame.shape

        # Scale up the width slightly to be able to detect aruco codes.
        # Don't scale up too much, since that severely impacts performance
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, int(width*1.3))
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))

        # Find the aruco codes over multiple frames.
        # `Detection.aruco()` automatically sets the detected table size after a certain amount of frames.
        for i in range(0, self.calibration_frames):
            nextFrame, frame = self.video.read()
            self.detector.aruco(frame)
        self.detector.calibrate(frame)

    def run(self, video):
        """Runs a game locally"""
        self.video = video
        self.calibrate()
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
        self.calibrate(video)
        # Set to input feed FPS
        video.set(cv2.CAP_PROP_FPS, 60)
        while True:
            nextFrame, frame = self.getFrame(video)
            # Send error image in case video feed does not work
            if not nextFrame:
                print("No frame")
                frame = cv2.imread("../website/Error_mirrored.jpg")
            frame = self.detector.detect(frame)
            # Encode frame for website
            ret, jpeg = cv2.imencode('.jpg', frame)
            self.buffer.append(jpeg)
            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    def getFrame(self, video):
        """Reads a frame from the video input and cuts it to the correct size"""
        self.time += 1
        nextFrame, frame = video.read()
        if nextFrame:
            frame = frame[self.detector.min_y:self.detector.max_y, self.detector.min_x:self.detector.max_x]
        return nextFrame, frame

    def buffer_frames(self):
        while True:
            bframes = self.buffer.copy()
            for jpeg in bframes:
                time.sleep(0.01)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')

    def add_goal(self, Left):
        """pass True if one goal should be added to the score of the left goal,
        else 1 will be added to the right goal"""
        self.website.add_goal(Left)

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
                self.detector.corners = [[]]*4
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
