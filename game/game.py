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
        self.detector = Detection(game=self)
        self.mode = Mode.NORMAL
        self.paused = False
        self.skip_frames = 0
        self.skip_range = [ord(f'{x}') for x in range(1, 10)]
        self.time = 0
        self.back_frames = []
        self.front_frames = []
        self.max_back_frames = self.detector.fps
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
            elif key == ord('s'):
                self.detector.max_ball_speed = 0
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

    def kalmanFilter(self):
        pass

    def stream(self):
        pass

    def run(self):
        while True:
            video = cv2.VideoCapture('data/video/best yet.mp4')
            nextFrame = True
            while nextFrame:

                if not self.paused:
                    nextFrame, frame = self.getFrame(video)
                    frame = self.detector.run(frame, self.mode)

                elif self.skip_frames > 0:
                    for i in range(0, self.skip_frames):
                        nextFrame, frame = self.getFrame(video)
                        if nextFrame == False: break
                    frame = self.detector.run(frame, self.mode)
                    self.skip_frames = 0

                else:
                    # Paused and mode change, only show the change
                    self.showFrame(self.detector.applyMode(self.mode, frame))
                    continue

                # elif self.skip_frames < 0 and 0 < len(self.back_frames) < self.max_back_frames:
                #     print(len(self.back_frames))
                #     self.front_frames.append(frame)
                #     frame = self.back_frames[-1]
                #     frame = self.detector.run(frame, self.mode)
                #     self.back_frames = self.back_frames[:-1]
                #     self.skip_frames = 0

                if nextFrame == False:
                    break                
                if DEBUG: self.showFrame(frame)
            
            # video.release()
            # cv2.destroyAllWindows()

    def getFrame(self, video_feed):
        # if len(self.front_frames) > 0:
        #     self.back_frames.append(frame)
        #     frame = self.front_frames[-1]
        #     self.front_frames = self.front_frames[:-1]
        #     return frame
        self.time += 1
        # if len(self.back_frames) >= self.max_back_frames:
        #     self.back_frames = self.back_frames[len(self.back_frames)-self.max_back_frames+1:]
        nextFrame, frame = video_feed.read()
        # if nextFrame: self.back_frames.append(frame)
        return nextFrame, frame

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
                frame = jpeg.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       frame + b'\r\n')
