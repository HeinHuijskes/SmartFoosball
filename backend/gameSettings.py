from collections import deque
from backend.misc import Mode


class GameSettings:
    def __init__(self):
        self.score_red = 0
        self.score_blue = 0
        self.mode = Mode.NORMAL
        self.paused = False
        self.skip_frame = False
        self.time = 0
        self.video_frames = []
        self.video = None
        self.calibration_frames = 10
        self.fps = 75 #TODO what do we think of these values? will this work with faster fps?
        self.delaysec = 5
        self.buffer_max_len = self.fps * self.delaysec #this value determines the delay
        self.buffer = deque(maxlen=(self.fps * self.delaysec))
        self.max_speed = [1]
        self.average_speed = [1]