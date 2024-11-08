from collections import deque
from backend.misc import Mode


class GameSettings:
    def __init__(self, debug=False):
        self.score_red = 0
        self.score_blue = 0
        self.mode = Mode.NORMAL
        self.paused = False
        self.skip_frame = False
        self.time = 0
        self.video_frames = []
        self.video = None
        self.calibration_frames = 60
        self.fps = 40
        self.delaysec = 5
        self.buffer_max_len = self.fps * self.delaysec  # This value determines the delay
        self.buffer = deque(maxlen=(self.fps * self.delaysec))
        self.max_speed = [1]
        self.average_speed = [1]
        self.debug = debug