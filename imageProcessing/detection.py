import cv2
import math
import random
import numpy as np
from ultralytics import YOLO
import time
from imageProcessing.misc import Mode, Contour, Colour


class Detection:
    """Class for object detection in a frame, based on colour differences."""

    def __init__(self, game):
        self.game = game
        # Minimum and maximum amount of pixels to consider a set of pixels a foos-man
        self.foos_men_min = 500
        self.foos_men_max = 5000
        self.table_length = 126  # cm
        self.pixel_width_cm = 0
        self.fps = 60
        self.zoom_levels = [1, 1.5, 2, 4, 6, 8, 10]  # amount of x zoom
        self.zoom = 0  # counter for choosing a zoom level
        self.last_known_ball_position = [0, 0]
        self.time = 0

        # Ball variables
        self.ball_min = 100
        self.ball_max = 1000
        self.ball_frames = 10
        self.ball_positions = [[]]*(self.ball_frames+1)
        self.max_ball_speed = 0

        # Parameters for video calibration
        # The corners of the playing field, frames since calibration, and angle rotation matrix
        self.corners = [[], [], [], []]
        self.frames = 0
        self.rotate_matrix = []
        self.min_x, self.max_x, self.min_y, self.max_y = 0, 0, 0, 0
        self.mid_x, self.mid_y = 0, 0
        self.time = time.perf_counter()

        # Settings
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        self.model = YOLO("./runs/detect/train1/weights/best.pt")
        self.model.to('cuda')
        self.classNames = ["balls"]

    def timer(self):
        own_time = self.game.time
        seconds = own_time // self.fps
        minutes = own_time // (self.fps * 60)
        frames = own_time % self.fps
        actual_time = time.perf_counter() - self.time
        print(f'Difference: {seconds - actual_time}')

    def run(self, frame):
        # frame = self.scale(frame, 0.5)
        # frame = self.aruco(frame)
        frame = self.ballDetectionYOLO(frame)
        frame = self.draw_ball_positions(frame)
        frame = self.drawTexts(frame)
        # if self.game.time % 25 == 0:
        #     self.timer()
        return frame

    def run_debug(self, frame, mode=Mode.NORMAL):
        cv2.rotate(frame, cv2.ROTATE_180, frame)
        # Detect corners and crop the frame
        frame = self.aruco(frame)
        # Scale the frame to fit within one laptop screen
        frame = self.scale(frame, 1)
        # Draw the ball tracer each frame
        frame = self.draw_ball_positions(frame)
        # Run foosmen detection and apply to frame
        frame = self.foosMenDetection(frame)

        # Run ball detection and apply to frame
        # frame = self.ballDetectionMask(frame, Colour.CORK)
        frame = self.ballDetectionYOLO(frame)

        # Apply colour mode for different colour detection highlights
        frame = self.applyMode(mode, frame)
        # Draw info texts on screen
        frame = self.drawTexts(frame)
        return frame

    def applyMode(self, mode, frame_normal):
        """Apply different colour modes to the frame. Options are BLUE, RED, FUNK, and NORMAL"""
        frame = self.zoom_in(frame_normal)
        if mode == Mode.BLUE:
            # Get the blue colour mask
            mask = self.colour_mask(frame, Colour.BLUE)
        elif mode == Mode.RED:
            # Get the red colour mask
            mask = self.colour_mask(frame, Colour.RED)
        elif mode == Mode.ORANGE:
            mask = self.colour_mask(frame, Colour.CORK)
        elif mode == Mode.FUNK:
            # Combine the red and blue colour masks
            red_mask = self.colour_mask(frame, Colour.RED)
            blue_mask = self.colour_mask(frame, Colour.BLUE)
            orange_mask = self.colour_mask(frame, Colour.ORANGE)
            mask = red_mask | blue_mask | orange_mask
        elif mode == Mode.DISCO:
            # Currently double zooms due to messy code order (not too bad, this is an unimportant mode anyway)
            frame = self.applyMode(random.choice([Mode.BLUE, Mode.RED, Mode.ORANGE, Mode.FUNK, Mode.NORMAL]), frame_normal)
            return frame
        else:
            # Apply no colour masks
            return frame

        return cv2.bitwise_and(frame, frame, mask=mask)
    
    def zoom_in(self, frame):
        if self.zoom == 0:
            return frame

        height, width, _ = frame.shape
        coords = self.last_known_ball_position
        size = int(width / self.zoom_levels[self.zoom])

        min_x, max_x = coords[0] - size, coords[0] + size
        min_x = max(min(min_x, max_x - size*2), 0)
        max_x = min(max(max_x, min_x + size*2), width)

        min_y, max_y, = coords[1] - size, coords[1] + size
        min_y = max(min(min_y, max_y - size*2), 0)
        max_y = min(max(max_y, min_y + size*2), height)

        frame = frame[min_y:max_y, min_x:max_x]
        # frame = self.scale(frame, 1/self.zoom_levels[self.zoom])

        return frame

    def aruco(self, frame):
        """Find the ArUco corners on a frame and store them"""
        # Convert to grayscale, invert colours
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        # Up the contrast
        cv2.convertScaleAbs(inverted, inverted, 3)
        # Detect ArUco markers
        (corners, ids, rejected) = self.detector.detectMarkers(inverted)
        if ids is not None:
            ids = ids.flatten()
            # cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for (marker, marker_id) in zip(corners, ids):
                # Reshape corner to a usable array of 4 corners, each with 2 coordinates (x,y)
                corner = marker.reshape((4, 2))
                maximum = 0
                for (x, y) in corner:
                    # Calculate the distance to the centre of the screen for every corner
                    distance = math.sqrt((x - self.mid_x) ** 2 + (y - self.mid_y) ** 2)
                    if distance > maximum:
                        maximum = distance
                        cx = x
                        cy = y
                if len(corners[0][0]) == 4:
                    self.corners[marker_id].append([cx, cy])

    def calibrate(self, frame):
        """Calibrate frame and rotate according to aruco corners"""
        result = []
        # Calculate the average positions of the stored inside corners
        print(self.corners)
        for corner in self.corners:
            if len(corner) == 0:
                print('NO CORNERS!')
                return
            average_x = sum([x for (x, y) in corner]) / len(corner)
            average_y = sum([y for (x, y) in corner]) / len(corner)
            result.append((average_x.item(), average_y.item()))

        # Calculate the amount of cdetected
        detected_corners = sum([len(corner) for corner in self.corners])
        confidence = min(detected_corners / 4 * 10000 // 100 / 5, 100)
        print(
            f'Corner confidence: {confidence}% ({detected_corners} corners detected in {5} frames)'
        )

        self.corners = result

        # Calculate the edges of the playing field according to corners calculated earlier
        self.min_x = int(min(self.corners[1][0], self.corners[2][0]))
        self.max_x = int(max(self.corners[3][0], self.corners[0][0]))
        self.min_y = int(min(self.corners[2][1], self.corners[3][1]))
        self.max_y = int(max(self.corners[1][1], self.corners[0][1]))
        print(self.corners)

        # Calculate the angle of the playing field compared to the x-axis
        angle = -int(math.degrees(
            math.atan(abs(self.corners[2][1] - self.corners[3][1]) / abs(self.corners[2][0] - self.corners[3][0]))))
        # Calculate a rotation matrix according to the rotation angle
        self.rotate_matrix = cv2.getRotationMatrix2D((self.mid_x, self.mid_y), angle, 1)

        frame = cv2.warpAffine(frame, self.rotate_matrix, frame.shape[1::-1], flags=cv2.INTER_LINEAR)
        frame = frame[self.min_y:self.max_y, self.min_x:self.max_x]
        height, width, _ = frame.shape
        self.pixel_width_cm = self.table_length / width

    def setDimensions(self, frame):
        """Sets the dimensions and middle point of the video feed"""
        height, width, _ = frame.shape
        # Takes width of input frame and determines horizontal middle point
        self.min_x = 0
        self.max_x = width
        self.mid_x = math.ceil(width * 0.5)
        # Takes height of input frame and determines vertical middle point
        self.min_y = 0
        self.max_y = height
        self.mid_y = math.ceil(height * 0.5)

    def ballDetectionYOLO(self, frame):
        position = []
        result = self.model.predict(frame, verbose=False)
        if result and result[0].boxes:
            boxes = result[0].boxes
            box = boxes[0]

            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            # frame = cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 0, 255), 2)
            # conf = math.ceil((box.conf[0] * 100)) / 100
            # cls = box.cls[0]
            # name = classNames[int(cls)]
            # cv2.putText(frame, f'{name} {conf}', (max(0, x1), max(35, y1)), 1, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # frame = cv2.circle(frame, (x1+w//2, y1+h//2), 1, Contour.RED, 2)
            position = [x1 + w // 2, y1 + h // 2]
        self.add_ball_position(position)
        return frame

    def ballDetectionMask(self, frame, colour):
        """Finds the ball, returns the frame and found ball coordinates"""
        orange_mask = self.colour_mask(frame, colour)
        frame, contours = self.contour_frame(frame, orange_mask, self.ball_min, self.ball_max, Contour.ORANGE)
        max_size = 0
        biggest = None
        height, width, _ = frame.shape

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if x < 150 or x > width - 150:
                continue

            area = cv2.contourArea(contour)
            if area > max_size:
                biggest = contour
                max_size = area

        if biggest is not None:
            x, y, w, h = cv2.boundingRect(biggest)
            x, y = x+w//2, y+h//2
            frame = cv2.circle(frame, (x, y), 1, Contour.RED, 2)
            # frame = cv2.circle(frame, (150, height//2), 15, Contour.BLUE, 3)

            self.add_ball_position([x, y])
            self.last_known_ball_position = [x, y]

        else:
            self.add_ball_position([])
            # self.kalman()

        return frame

    def kalman(self):
        last_position = self.ball_positions[-1]
        if len(last_position) < 3:
            self.add_ball_position([])
            return
        
        # print(last_position)
        speed_vector = last_position[3]
        prediction = [last_position[0] + speed_vector[0], last_position[1] + speed_vector[1], last_position[2], speed_vector]
        self.add_ball_position(prediction)

    def add_ball_position(self, position):
        old_position = self.ball_positions[-1]
        if len(position) != 0 and len(old_position) != 0:
            pixel_speed = math.sqrt((position[0]-old_position[0])**2 + (position[1]-old_position[1])**2)
            position.append(pixel_speed)
            if pixel_speed > self.max_ball_speed and self.pixel_width_cm != 0:
                # speed = pixel_speed * self.pixel_width_cm / 100 * self.fps * 3.6
                # print(speed, pixel_speed)
                # if speed < 75:  # TODO: Remove the need for this restraint
                self.max_ball_speed = pixel_speed
            position.append((position[0]-old_position[0], position[1]-old_position[1]))
        self.ball_positions.append(position)
        return

    def draw_ball_positions(self, frame):
        # print(self.ball_positions)
        old_position = self.ball_positions[-self.ball_frames]
        for position in self.ball_positions[-self.ball_frames:]:
            if len(position) == 0 or len(old_position) == 0:
                continue
            colour = Contour.BLACK
            # if len(position) > 2:
            #     colour = [c*min((position[2])/100, 1)//1 for c in colour]
            #     print(colour)
            frame = cv2.line(frame, old_position[:2], position[:2], colour, 2)
            old_position = position
        return frame
    
    def drawTexts(self, frame):
        height, width, _ = frame.shape
        speed = self.max_ball_speed * self.pixel_width_cm / 100 * self.fps * 100 // 1 / 100
        speed_kmh = speed*3.6*100//1/100
        cv2.putText(frame, f'Max speed: {speed} m/s ({speed_kmh} km/h)', (width//4, 50), 1, 1, Contour.BLACK, 2, cv2.LINE_AA)

        time = self.game.time
        seconds = time // self.fps
        minutes = time // (self.fps*60)
        frames = time % self.fps
        cv2.putText(frame, f'Time: {minutes}m {seconds}s {frames}f', (width//4*3, 50), 1, 1, Contour.BLACK, 2, cv2.LINE_AA)
        return frame

    def foosMenDetection(self, frame):
        """Looks for blue and red, and returns their outlines on the frame."""
        # cv2.convertScaleAbs(frame, frame, 2)
        blue_mask = self.colour_mask(frame, Colour.BLUE)
        red_mask = self.colour_mask(frame, Colour.RED)

        frame, _ = self.contour_frame(frame, blue_mask, self.foos_men_min, self.foos_men_max, Contour.BLUE)
        frame, _ = self.contour_frame(frame, red_mask, self.foos_men_min, self.foos_men_max, Contour.RED)


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
        resize = (math.ceil(width / scaler), math.ceil(height / scaler))
        frame = cv2.resize(frame, resize)
        return frame
