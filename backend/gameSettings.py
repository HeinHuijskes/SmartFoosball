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
        self.calibration_frames = 5
        self.fps = 60
        self.delaysec = 5
        self.buffer = deque(maxlen=(self.fps * self.delaysec))