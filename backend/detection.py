import cv2
import math
import random
import numpy as np
from backend.detectionSettings import DetectionSettings
import time
from backend.misc import Mode, Contour, Colour


class Detection(DetectionSettings):
    """Class for object detection in a frame, based on colour differences."""

    def __init__(self, game):
        super().__init__()
        self.game = game

    def detect(self, frame):
        """
        Run basic detection on a frame and update the time.
        Apply YOLO to find the ball, draw all last known ball positions as a line, display text information and scale.
        Works best with a pre-cropped frame displaying only a foosball table, though not strictly required.
        """
        self.updateTime()
        frame = self.ballDetectionYOLO(frame)
        frame = self.draw_ball_positions(frame)
        self.detect_zone()
        frame = self.drawTexts(frame)
        print("ball speed", self.ball_speed)
        return frame, self.ball_speed

    def detect_debug(self, frame, mode=Mode.NORMAL):
        """Run basic detection with added debug features. See also `Detection.detect()`."""
        if mode == Mode.DISCO:
            mode = random.choice([Mode.BLUE, Mode.RED, Mode.FUNK, Mode.NORMAL])
        # cv2.rotate(frame, cv2.ROTATE_180, frame)
        self.blue_mask = self.colour_mask(frame, Colour.BLUE)
        self.red_mask = self.colour_mask(frame, Colour.RED)
        mask = self.selectMask(mode)

        # Run regular ball detection
        frame = self.detect(frame)

        # Temporary possession zone stuff
        # height, width, _ = frame.shape
        # for i in self.rod_middles:
        #     frame = cv2.line(frame, (int(i / self.pixel_width_cm), 0),
        #                      (int(i / self.pixel_width_cm), height), Colour.BLACK, 5)
        # for i in self.zones:
        #     frame = cv2.line(frame, (int(i[0] / self.pixel_width_cm), 0),
        #                      (int(i[0] / self.pixel_width_cm), height), Colour.BLACK, 5)
        #     frame = cv2.line(frame, (int(i[1] / self.pixel_width_cm), 0),
        #                      (int(i[1] / self.pixel_width_cm), height), Colour.BLACK, 5)

        # Apply the colour mask to the frame
        frame = cv2.bitwise_and(frame, frame, mask=mask)
        frame = self.foosMenDetection(frame, mode)
        frame = self.zoom_in(frame)
        frame = self.scale(frame, 0.5)

        return frame

    def updateTime(self):
        """Update the current FPS every 60 frames. Calculates the average FPS over the elapsed time."""
        if self.game.time % 60 != 0:
            return
        time_elapsed = time.perf_counter_ns() - self.frame_time
        # time_elapsed is in nanoseconds, so divide by 10^9, and by 60 for the past 60 frames
        self.fps = 1 / (time_elapsed / 1000000000 / 60)
        # Update latest current time
        self.frame_time = self.frame_time + time_elapsed

    def selectMask(self, mode):
        """Create different colour masks for the frame. Options are BLUE, RED, FUNK, and NORMAL"""
        if mode == Mode.BLUE:
            # Get the blue colour mask
            mask = self.blue_mask
        elif mode == Mode.RED:
            # Get the red colour mask
            mask = self.red_mask
        elif mode == Mode.FUNK:
            # Combine the red and blue colour masks
            mask = self.red_mask | self.blue_mask
        else:
            # Apply no colour masks
            return None
        return mask
    
    def aruco(self, frame):
        """Find the ArUco corners on a frame and store them"""
        # Convert to grayscale, invert colours
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        # Up the contrast
        cv2.convertScaleAbs(inverted, inverted, 3)
        # Detect ArUco markers
        (corners, ids, rejected) = self.detector.detectMarkers(inverted)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        height, width, _ = frame.shape
        mid_x, mid_y = width / 2, height / 2
        if ids is not None:
            ids = ids.flatten()

            for (marker, marker_id) in zip(corners, ids):
                corner = marker.reshape((4, 2))
                # Reshape corner to a usable array of 4 corners, each with 2 coordinates (x,y)
                maximum = 0
                for (x, y) in corner:
                    # Calculate the distance to the centre of the screen for every corner
                    distance = math.sqrt((x - mid_x) ** 2 + (y - mid_y) ** 2)
                    if distance > maximum:
                        maximum = distance
                        cx = x
                        cy = y
                if len(corners[0][0]) == 4:
                    self.corners[marker_id] = [cx, cy]

    def calibrate(self, frame):
        """Calibrate frame and rotate according to aruco corners"""
        # Calculate the average positions of the stored inside corners
        self.calibrated = False
        corners = [i for i, corner in enumerate(self.corners) if len(corner) > 0]
        if len(corners) < 4:
            print(f'ONLY {len(corners)} CORNERS DETECTED! NEEDED 4!')
            print(f'Missing corners {corners}')
            height, width, _ = frame.shape
            self.max_x, self.max_y = width, height
            return

        if not self.calculateCorners():
            return

        # Calculate a rotation matrix according to the rotation angle
        self.rotate_matrix = cv2.getRotationMatrix2D((self.mid_x, self.mid_y), -math.degrees(self.angle), 1)
        frame = cv2.warpAffine(frame, self.rotate_matrix, frame.shape[1::-1])
        # Crop frame
        frame = frame[self.min_y:self.max_y, self.min_x:self.max_x]
        height, width, _ = frame.shape
        self.pixel_width_cm = self.table_length / width
        self.calibrated = True

    def calculateCorners(self):
        # Calculate the edges of the playing field according to corners calculated earlier
        self.min_x = int(min(self.corners[2][0], self.corners[0][0]))
        self.max_x = int(max(self.corners[0][0], self.corners[2][0]))
        self.min_y = int(min(self.corners[2][1], self.corners[0][1]))
        self.max_y = int(max(self.corners[0][1], self.corners[2][1]))
        if self.min_x >= self.max_x:
            return False

        # Calculate middle point of target frame
        self.mid_x = self.min_x + (self.max_x - self.mid_x) // 2
        self.mid_y = self.min_y + (self.max_y - self.mid_y) // 2

        self.correctAngle()

        return True

    def correctAngle(self):
        # Calculate correct corner coordinates in the newly rotated frame
        # Consider a circle along which the coordinates are rotated. Easiest to calculate is a circle around the origin,
        # so we shift the x and y values to the origin first (e.g. "(self.min_x-self.mid_x)").
        # Then we calculate the rotated points, e.g. (x1, y1) rotates clockwise with angle θ to (x2, y2):
        # x2 = x1*cos(θ) + y1*sin(θ), and y2 = -x1*sin(θ) + y1*cos(θ)
        # Finally the mid_x and mid_y values are added again to return to the point in the frame, not around the origin.
        # See also https://math.stackexchange.com/questions/260096/find-the-coordinates-of-a-point-on-a-circle.

        # Calculate the angle of the playing field compared to the x-axis
        opposite = abs(self.corners[2][1] - self.corners[3][1])
        side = abs(self.corners[2][0] - self.corners[3][0])
        self.angle = math.atan(opposite / side)
        if self.angle < 0:
            self.angle += 2 * math.pi

        angle = self.angle
        a_x = self.mid_x
        a_y = self.mid_y
        b_x = self.corners[2][0]
        b_y = self.corners[2][1]
        e_x = self.corners[0][0]
        e_y = self.corners[0][1]

        c_x = a_x + (b_x - a_x) * math.cos(angle) - (b_y - a_y) * math.sin(angle)
        c_y = a_y + (b_x - a_x) * math.sin(angle) + (b_y - a_y) * math.cos(angle)

        d_x = a_x + (e_x - a_x) * math.cos(angle) - (e_y - a_y) * math.sin(angle)
        d_y = a_y + (e_x - a_x) * math.sin(angle) + (e_y - a_y) * math.cos(angle)

        self.min_x = int(min(d_x, c_x))
        self.min_y = int(min(d_y, c_y))
        self.max_x = int(max(d_x, c_x))
        self.max_y = int(max(d_y, c_y))

        return

    def ballDetectionYOLO(self, frame):
        result = self.model.predict(frame, verbose=False)
        if result and result[0].boxes:
            boxes = result[0].boxes
            box = boxes[0]
            # confidence = box.conf
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            position = [x1 + w // 2, y1 + h // 2]
            self.kalman_count = 0
        else:
            position = self.kalman()
        self.add_ball_position(position)
        return frame

    def kalman(self):
        last_position = self.ball_positions[-1]
        if len(last_position) < 3 or self.kalman_count > 8:
            return []
        speed_vector = last_position[3]
        prediction = [last_position[0] + speed_vector[0], last_position[1] + speed_vector[1], last_position[2], speed_vector]
        self.kalman_count += 1
        return prediction

    def add_ball_position(self, position):
        old_position = self.ball_positions[-1]
        if len(position) != 0:
            self.last_known_position = position

        if len(position) != 0 and len(old_position) != 0:
            pixel_speed = math.sqrt((position[0]-old_position[0])**2 + (position[1]-old_position[1])**2)

            speed = pixel_speed * self.pixel_width_cm / 100 * self.fps
            print("pixel width: ", self.pixel_width_cm)
            position.append(pixel_speed)
            if speed > self.max_ball_speed and self.pixel_width_cm != 0:
                self.max_ball_speed = speed
                print("max_speed", self.max_ball_speed)
            # extra line to get speed
            if self.pixel_width_cm != 0:
                self.ball_speed = speed * 100 // 1 / 100 #m/s
                print("ball_speed", self.ball_speed)
            position.append((position[0]-old_position[0], position[1]-old_position[1]))
        self.ball_positions.append(position)
        return

    def draw_ball_positions(self, frame):
        old_position = self.ball_positions[-self.ball_frames]
        for position in self.ball_positions[-self.ball_frames:]:
            if len(position) == 0 or len(old_position) == 0:
                continue
            colour = Contour.BLACK
            frame = cv2.line(frame, old_position[:2], position[:2], colour, 2)
            old_position = position
        return frame

    def drawTexts(self, frame):
        """Draws FPS and maximum speed on the frame"""
        self.fps = max(int(self.fps), 1)

        height, width, _ = frame.shape
        speed = self.max_ball_speed * 100 // 1 / 100
        speed_kmh = speed*3.6*100//1/100
        cv2.putText(frame, f'Max speed: {speed} m/s ({speed_kmh} km/h)', (0, 50), 1, 1, Contour.BLACK, 2, cv2.LINE_AA)
        cv2.putText(frame, f'FPS: {self.fps}', (width//4*3, 50), 1, 1, Contour.BLACK, 2, cv2.LINE_AA)
        return frame
    
    def zoom_in(self, frame):
        """Zooms in on the ball with specified zoom level"""
        if self.zoom == 0:
            return frame

        height, width, _ = frame.shape
        coords = self.last_known_position
        # Calculates window size
        size = int(width / self.zoom_levels[self.zoom])
        # Calculates x and y coordinates of window based on ball coordinates
        min_x, max_x = coords[0] - size, coords[0] + size
        min_x = max(min(min_x, max_x - size*2), 0)
        max_x = min(max(max_x, min_x + size*2), width)

        min_y, max_y, = coords[1] - size, coords[1] + size
        min_y = max(min(min_y, max_y - size*2), 0)
        max_y = min(max(max_y, min_y + size*2), height)

        frame = frame[min_y:max_y, min_x:max_x]
        frame = self.scale(frame, self.zoom_levels[self.zoom] / 3)
        return frame

    def foosMenDetection(self, frame, mode):
        """Looks for blue and red, and returns their outlines on the frame."""
        if not mode == Mode.RED:
            frame, _ = self.contour_frame(frame, self.blue_mask, self.foos_men_min, self.foos_men_max, Contour.BLUE)
        if not mode == Mode.BLUE:
            frame, _ = self.contour_frame(frame, self.red_mask, self.foos_men_min, self.foos_men_max, Contour.RED)
        return frame

    def contour_frame(self, frame, mask, area_min=100, area_max=1000, contour_colour=Contour.BLACK):
        """Colour all contours in a mask depending on a minimum and maximum area.
        Return the frame with contour lines."""
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_list = []
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area_min <= area <= area_max:
                x, y, w, h = cv2.boundingRect(contour)
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), contour_colour, 2)
                contour_list.append(contour)
        return frame, contour_list

    def colour_mask(self, frame, colour):
        """Obtain the mask of colours in a frame."""
        # Convert frame to hsv
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Create a colour mask of the frame, only keeping colour between a specified range
        mask = cv2.inRange(hsvFrame, colour[0], colour[1])
        # Apply a kernel to the mask
        kernel = np.ones((5, 5), "uint8")
        mask = cv2.dilate(mask, kernel)
        return mask

    def scale(self, frame, scaler=2):
        """Resize a frame according to preference in order to fit onto a laptop screen"""
        height, width, _ = frame.shape
        resize = (int(width * scaler), int(height * scaler))
        frame = cv2.resize(frame, resize)
        return frame

    def detect_zone(self):
        """Detect whether the ball is currently in a possession zone, and whether it has been for too long"""
        if not self.last_known_position == [0, 0]:
            new_zone = self.get_zone()
            if new_zone != self.possession_zone or new_zone == -1:
                self.possession_timer = time.time()
            else:
                if time.time() - self.possession_timer > 15.0:
                    print("Let go of that ball!!!")
            self.possession_zone = new_zone

    def get_zone(self):
        """Detect what possession zone the ball is currently in (-1 if none)"""
        x = self.last_known_position[0] * self.pixel_width_cm
        for i, z in enumerate(self.zones):
            if z[0] <= x <= z[1]:
                return i
        return -1
