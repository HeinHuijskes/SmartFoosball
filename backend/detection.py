import cv2
import math
import random
import numpy as np
from backend.detectionSettings import DetectionSettings
import time
from backend.misc import Mode, Contour, Colour
from playsound import playsound


class Detection(DetectionSettings):
    """Class for object detection in a frame, based on colour differences."""

    def __init__(self, game):
        self.game = game
        super().__init__()

    def detect(self, frame):
        """
        Run basic detection on a frame and update the time.
        Apply YOLO to find the ball, draw all last known ball positions as a line, display text information and scale.
        Works best with a pre-cropped frame displaying only a foosball table, though not strictly required.
        """
        self.update_time()
        self.ball_detection_YOLO(frame)
        self.detect_zone()

        # If the ball changes direction, find out if a foosman kicked it
        if self.detect_kick():
            self.kicker = self.find_kicker(frame)
            if self.kicker == "Dennis Bergkamp":
                playsound('data/fifa/Voicy_Dennis Bergkamp Goal.mp3', block=False)
        else:
            self.kicker = None

        self.draw_ball_positions(frame)
        return frame

    def detect_debug(self, frame, mode=Mode.NORMAL):
        """Run basic detection with added debug features. See also `Detection.detect()`."""
        if mode == Mode.DISCO:
            mode = random.choice([Mode.BLUE, Mode.RED, Mode.FUNK, Mode.NORMAL])
        self.blue_mask = self.colour_mask(frame, Colour.BLUE)
        self.red_mask = self.colour_mask(frame, Colour.RED)
        mask = self.select_mask(mode)

        # Run regular ball detection
        frame = self.detect(frame)
        if self.kicker:
            print(f"Kicked by: {self.kicker}")

        frame = cv2.bitwise_and(frame, frame, mask=mask)
        frame, _ = self.foos_men_detection(frame, mode)
        frame = self.draw_texts(frame)
        frame = self.zoom_in(frame)
        frame = self.scale(frame, 0.5)

        return frame

    def update_time(self):
        """Update the current FPS every 60 frames. Calculates the average FPS over the elapsed time."""
        # Only update the FPS after a specified number of frames have passed
        if self.game.time % self.fps_update_speed != 0:
            return

        time_elapsed = time.perf_counter_ns() - self.frame_time
        # time_elapsed is in nanoseconds, so divide by 10^9, and by amount of passed frames
        self.fps = 1 / (time_elapsed / 1000000000 / self.fps_update_speed)
        self.frame_time = self.frame_time + time_elapsed
        return

    def select_mask(self, mode):
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
        # Convert to grayscale, invert colours, and up the contrast to detect ArUco more easily
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        cv2.convertScaleAbs(inverted, inverted, 3)

        (corners, ids, rejected) = self.aruco_detector.detectMarkers(inverted)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        height, width, _ = frame.shape
        mid_x, mid_y = width / 2, height / 2
        if ids is not None:
            ids = ids.flatten()

            # Iterate over detected corners
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
                # Check that there are 4 corners detected, and store each corner in the correct spot
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

        # Calculate a rotation matrix according to the rotation angle, then rotate
        self.rotate_matrix = cv2.getRotationMatrix2D((self.mid_x, self.mid_y), -math.degrees(self.angle), 1)
        frame = cv2.warpAffine(frame, self.rotate_matrix, frame.shape[1::-1])

        # Crop the frame
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
        if self.corners[2][1] < self.corners[3][1]:
            self.angle = math.atan(opposite / side)
        else:
            self.angle = -math.atan(opposite / side)

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

    def ball_detection_YOLO(self, frame):
        """Use Yolo model and save predicted ball location"""
        result = self.model.predict(frame, verbose=False)
        # Get the result with the highest confidence (so the first one)
        if result and result[0].boxes:
            boxes = result[0].boxes
            box = boxes[0]
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            position = [x1 + w // 2, y1 + h // 2]
            self.kalman_count = 0
        else:
            # If there are no results, use Kalman filter
            position = self.kalman()
        self.add_ball_position(position)
        return

    def kalman(self):
        """Use Kalman filter to predict a new ball position"""
        last_position = self.ball_positions[-1]
        # Check if there are enough recent ball positions to predict,
        # and there have not been too many Kalman predictions in a row
        if len(last_position) < 3 or self.kalman_count > self.kalman_max:
            return []
        speed_vector = last_position[3]
        prediction = [last_position[0] + speed_vector[0], last_position[1] + speed_vector[1], last_position[2],
                      speed_vector]
        self.kalman_count += 1
        return prediction

    def add_ball_position(self, position):
        """Store ball position and calculate speed"""
        old_position = self.ball_positions[-1]
        if len(position) != 0:
            self.last_known_position = position

        if len(position) != 0 and len(old_position) != 0:
            # Calculate speed and store if maximum ball speed
            pixel_speed = math.sqrt((position[0] - old_position[0]) ** 2 + (position[1] - old_position[1]) ** 2)

            speed = pixel_speed * self.pixel_width_cm / 100 * self.fps
            position.append(pixel_speed)
            if speed > self.max_ball_speed and self.pixel_width_cm != 0:
                self.max_ball_speed = speed
                if self.game.debug:
                    print(f"Updated max speed to {self.max_ball_speed}")
            # extra line to get speed
            if self.pixel_width_cm != 0:
                self.ball_speed = round(speed, 2)  # m/s
            position.append((position[0]-old_position[0], position[1]-old_position[1]))
        self.ball_positions.append(position)
        return

    def draw_ball_positions(self, frame):
        """Draw a line following the recent ball positions"""
        index = min(len(self.ball_positions), self.ball_frames)
        old_position = self.ball_positions[-index]
        for position in self.ball_positions[-index:]:
            if len(position) == 0 or len(old_position) == 0:
                old_position = position
                continue
            colour = Contour.BLACK
            frame = cv2.line(frame, old_position[:2], position[:2], colour, 2)
            old_position = position
        return

    def draw_texts(self, frame):
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
        if self.zoom_index == 0:
            return frame

        height, width, _ = frame.shape
        coords = self.last_known_position
        # Calculates window size
        size = int(width / self.zoom_levels[self.zoom_index])
        # Calculates x and y coordinates of window based on ball coordinates
        min_x, max_x = coords[0] - size, coords[0] + size
        min_x = max(min(min_x, max_x - size * 2), 0)
        max_x = min(max(max_x, min_x + size * 2), width)

        min_y, max_y, = coords[1] - size, coords[1] + size
        min_y = max(min(min_y, max_y - size * 2), 0)
        max_y = min(max(max_y, min_y + size * 2), height)

        frame = frame[min_y:max_y, min_x:max_x]
        frame = self.scale(frame, self.zoom_levels[self.zoom_index] / 3)
        return frame

    def foos_men_detection(self, frame, mode):
        """Looks for blue and red, and returns their outlines on the frame."""
        contoured_frame = frame.copy()
        if not mode == Mode.RED:
            contoured_frame, contours = self.contour_frame(contoured_frame, self.blue_mask, self.foos_men_min, self.foos_men_max, Contour.BLUE)
        if not mode == Mode.BLUE:
            contoured_frame, contours = self.contour_frame(contoured_frame, self.red_mask, self.foos_men_min, self.foos_men_max, Contour.RED)
        return contoured_frame, contours

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
        if self.last_known_position == [0, 0]:
            return

        new_zone = self.get_zone()
        # If in a new zone, reset possession timer and note statistics
        if new_zone != self.possession_zone or new_zone == -1:
            if self.possession_zone != -1:
                self.possessions[self.possession_zone] += time.time() - self.possession_timer
            self.possession_timer = time.time()
        else:
            # If not in a new zone, check for possession violation
            if 16.0 > time.time() - self.possession_timer > 15.0:
                if self.game.debug:
                    print("More than 15 seconds of possession! Let go of that ball!")
        self.possession_zone = new_zone

    def get_zone(self):
        """Detect what possession zone the ball is currently in (-1 if none)"""
        x = self.last_known_position[0] * self.pixel_width_cm
        for i, z in enumerate(self.zones):
            if z[0] <= x <= z[1]:
                return i
        return -1

    def detect_kick(self):
        """Detect when the ball has been kicked by a significant change in speed vector"""
        if len(self.ball_positions[-1]) > 2 and len(self.ball_positions[-2]) > 2:
            x, y = self.ball_positions[-1][3]
            old_x, old_y = self.ball_positions[-2][3]
            # Set x and/or y to 1 to prevent division by 0
            if x == 0:
                x = 1
            if y == 0:
                y = 1
            # Difference between old and new speed vector
            x_diff = abs((x - old_x) / x)
            y_diff = abs((y - old_y) / y)
            # Return true if significant difference in vectors
            if (x_diff > 4.0 or y_diff > 4.0) and self.possession_zone != -1:
                self.last_kick_position = self.ball_positions[-1]
                return True
        return False

    def find_kicker(self, frame):
        """Find the foosman who last kicked the ball"""
        ball_y = self.last_kick_position[1]
        z = self.possession_zone

        # Check which side has possession of the ball, then retrieve contours for that colour
        if z in [0, 1, 3, 5]:  # blue
            mode = Mode.BLUE
            self.blue_mask = self.colour_mask(frame, Colour.BLUE)
        else:
            mode = Mode.RED
            self.red_mask = self.colour_mask(frame, Colour.RED)
        _, contours = self.foos_men_detection(frame, mode)
        self.red_mask, self.blue_mask = None, None

        foos_men = []
        zone = (self.zones[z][0] / self.pixel_width_cm, self.zones[z][1] / self.pixel_width_cm)
        # Loop over the contours and filter those that lie in the correct zone
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if zone[0] < (x + w/2) < zone[1]:
                foos_men.append(y + h/2)

        if len(foos_men) == 0:
            return "No kicker detected"  # No foos_man detected in this zone
        foos_men = sorted(foos_men)  # Sort the foos_men y-positions large to small

        best_y = abs(foos_men[0] - ball_y)
        index = 0
        # Loop over the candidates in the right zone, and find the one closest to the ball
        for i, y in enumerate(foos_men[1:]):
            test_y = abs(y - ball_y)
            if test_y < best_y:
                best_y = test_y
                index = i+1

        # Crop the index to avoid index overflow in case too many players are detected
        index = min(index, len(self.game.staticulator.players[z])-1)
        return self.game.staticulator.players[z][index]
