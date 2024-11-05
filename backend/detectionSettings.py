from ultralytics import YOLO
import time
import cv2


class DetectionSettings:
    def __init__(self):
        # Amount of frames Kalman Filter has been used for
        self.kalman_count = 0
        # Max number of frames to use Kalman Filter for
        self.kalman_max = 8

        # Minimum and maximum amount of pixel area to consider a set of pixels a foos-man
        self.foos_men_min = 500  # px
        self.foos_men_max = 5000  # px

        ## Table dimensions
        self.table_length = 126  # cm
        self.pixel_width_cm = 0  # cm/px
        self.min_x, self.max_x = 0, 0  # px
        self.min_y, self.max_y = 0, 0  # px
        self.mid_x, self.mid_y = 0, 0  # px

        # Corner coordinates detemined by ArUco codes, [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        self.corners = [[], [], [], []]  # [[px, px]]
        # Matrix of values that rotate the table to correct its angle
        self.rotate_matrix = []
        self.angle = 0
        # Zoom levels, zooms in centered on the ball
        self.zoom_levels = [1, 1.5, 2, 4, 6, 8, 10]
        # Index for current zoom level
        self.zoom_index = 0

        # Current FPS, sampled over multiple frames
        self.fps = 1  # f/s
        # Time since last frame sample
        self.frame_time = time.perf_counter_ns()  # ns
        # Amount of frames to wait before sampling FPS again
        self.fps_update_speed = 60

        # Amount of last known ball positions to store
        self.ball_frames = 30
        self.max_ball_speed = 0  # m/s
        # Current ball speed
        self.ball_speed = 0
        self.last_known_position = [0, 0]
        # Previous ball positions, [[x,y], [x,y], ...]
        self.ball_positions = [[]]  # [[px, px]]

        # Settings for aruco detection
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
        self.parameters = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        self.calibrated = False

        # Load custom trained YOLO object detection model
        self.model = YOLO("./runs/detect/LaserFog15/weights/best.pt")
        # Set the model to GPU with CUDA to run faster
        self.model.to('cuda')
        if self.game.debug:
            # The output of this print statement should be along the lines of "cuda:0", not "cpu"
            print(f'Model loaded on device: {self.model.device}')

        # Blue and red masks, used each frame to segment a frame into specific colours
        self.blue_mask = None
        self.red_mask = None

        # Different possession zones
        self.zones = 8 * [(0, 0)]
        # Rods are equidistant from each other, so the distance is always 15 cm (on the table)
        rod_distance = 15  # cm
        # Zone radius, so distance a foosman could still reach the ball from (6 cm)
        zone_range = 6  # cm
        # List of positions where the middle of different rods are, starting at 11 cm
        rod_middles = [11]  # [cm]

        # Initialize zone positions
        for i in range(len(self.zones) - 1):
            rod_middles.append(rod_middles[-1] + rod_distance)
        for i in range(len(self.zones)):
            self.zones[i] = (rod_middles[i] - zone_range, rod_middles[i] + zone_range)

        # Count how long the current zone has the ball, max is 15 seconds (official rules)
        self.possession_timer = time.time()
        # Current possession zone, -1 for none
        self.possession_zone = -1
        # Timer for possession times by each rod
        self.possessions = 8 * [0.0]
        # Last rod to kick the ball
        self.last_kick_position = None
        # List of past foosman who have kicked the ball
        self.kickers = []
        self.kicker = "No kicker detected" #the most recent kicker for the website

