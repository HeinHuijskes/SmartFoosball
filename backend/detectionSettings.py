from ultralytics import YOLO
import time
import cv2


class DetectionSettings:
    def __init__(self):
        self.kalman_count = 0
        # Minimum and maximum amount of pixel area to consider a set of pixels a foos-man
        self.foos_men_min = 500  # px
        self.foos_men_max = 5000  # px

        # Table dimensions
        self.table_length = 126  # cm
        self.pixel_width_cm = 0  # cm/px
        self.min_x, self.max_x = 0, 0  # px
        self.min_y, self.max_y = 0, 0  # px
        self.mid_x, self.mid_y = 0, 0  # px
        # Corner coordinates, [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]. Each corner list [x1,y1] is considered as a list of
        # detected candidates [[x1,y1], [x1,y1], ...] while calibrating. Afterward the average of this is taken.
        self.corners = [[], [], [], []]  # [[px, px]]
        # The rotate matrix contains values that re-align the angle of the table to be straight
        self.rotate_matrix = []
        self.angle = 0

        # Start fps is 1, this is later dynamically determined by measuring time per frame
        self.fps = 1  # f/s
        self.frame_time = time.perf_counter_ns()  # ns
        self.zoom_levels = [1, 1.5, 2, 4, 6, 8, 10]  # amount of x zoom in debug mode
        self.zoom = 0  # index for choosing a zoom level

        # Ball variables
        # Amount of last known ball positions to store
        self.ball_frames = 10
        # Last known ball positions, [[x,y], [x,y], ...]
        self.ball_positions = [[]] * (self.ball_frames + 1)  # [[px, px]]
        self.max_ball_speed = 0  # m/s
        self.last_known_position = [0, 0]

        # Settings for aruco detection
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

        # Load custom trained YOLO object detection model
        self.model = YOLO("./runs/detect/train1/weights/best.pt")
        # Set the model to GPU with CUDA to run faster
        # If this does not work, see README.md for a line on how to recompile/install pytorch with CUDA included
        self.model.to('cuda')
        # The output of this print statement should be along the lines of "cuda:0", not "cpu". It indicates success
        print(self.model.device)
        # Classnames to detect. Only allow YOLO to detect the "balls" class, which was custom trained in "best.pt".
        self.classNames = ["balls"]

        # Blue and red mask variables
        self.blue_mask = None
        self.red_mask = None
        self.calibrated = False

        # Possession zone detection settings
        self.possession_timer = time.time()
        self.possession_zone = -1       # Change to current possession zone, -1 for none

        self.zones = 8 * [(0, 0)]
        rod_distance = 15               # Rods seem to be equidistant from each other
        zone_range = 6
        self.rod_middles = [11]
        for i in range(len(self.zones) - 1):
            self.rod_middles.append(self.rod_middles[-1] + rod_distance)
        print(self.rod_middles)
        for i in range(len(self.zones)):
            self.zones[i] = (self.rod_middles[i] - 6, self.rod_middles[i] + 6)

        print(self.zones)

