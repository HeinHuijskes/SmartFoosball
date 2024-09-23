import cv2
import math
import random
import numpy as np

from imageProcessing.misc import Mode, Contour, Colour

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

DEBUG = True


class Detection:
    """Class for object detection in a frame, based on colour differences."""

    def __init__(self):
        # Minimum and maximum amount of pixels to consider a set of pixels a foos-man
        self.foos_men_min = 400
        self.foos_men_max = 3000

        # Parameters for video calibration
        # The corners of the playing field, frames since calibration, and angle rotation matrix
        self.corners = [[], [], [], []]
        self.frames = 0
        self.rotate_matrix = []
        self.min_x, self.max_x, self.min_y, self.max_y = 0, 0, 0, 0
        self.mid_x, mid_y = 0, 0

    def run(self, frame, mode=Mode.NORMAL):
        # Detect corners and crop the frame
        frame = self.aruco(frame)
        # Scale the frame to fit within one laptop screen
        frame = self.scale(frame, 1)
        # Apply colour mode for different colour detection highlights
        frame = self.applyMode(mode, frame)
        # Run foosmen detection and apply to frame
        return self.foosMenDetection(frame)

    def applyMode(self, mode, frame):
        """Apply different colour modes to the frame. Options are BLUE, RED, FUNK, and NORMAL"""
        if mode == Mode.BLUE:
            # Get the blue colour mask
            mask = self.colour_mask(frame, Colour.BLUE)
        elif mode == Mode.RED:
            # Get the red colour mask
            mask = self.colour_mask(frame, Colour.RED)
        elif mode == Mode.ORANGE:
            mask = self.colour_mask(frame, Colour.ORANGE)
        elif mode == Mode.FUNK:
            # Combine the red and blue colour masks
            red_mask = self.colour_mask(frame, Colour.RED)
            blue_mask = self.colour_mask(frame, Colour.BLUE)
            orange_mask = self.colour_mask(frame, Colour.ORANGE)
            mask = red_mask | blue_mask | orange_mask
        elif mode == Mode.DISCO:
            frame = self.applyMode(random.choice([Mode.BLUE, Mode.RED, Mode.ORANGE, Mode.FUNK, Mode.NORMAL]), frame)
            return frame
        else:
            # Apply no colour masks
            return frame

        return cv2.bitwise_and(frame, frame, mask=mask)

    def aruco(self, frame, calibration_time=5):
        """Detects aruco, returns the bounding box of the foosball table"""
        # Flip the frame (debug for selfie camera mode) TODO: remove
        # frame = cv2.flip(frame, 1)

        if self.frames == 0:
            # At the start of a stream, always set the dimensions to the full frame
            self.setDimensions(frame)

        elif self.frames < calibration_time:
            # While under a margin (calibration_time), measure ArUco codes every frame to calibrate
            self.measureCorners(frame)

        elif min([len(corner) for corner in self.corners]) < 1 and self.frames == calibration_time:
            # If not enough corners have been detected, but calibration is done, run calibration again
            self.frames = 0
            self.corners = [[], [], [], []]

        elif self.frames > calibration_time * 20:
            # After a set amount of time, always run calibration again
            self.frames = 0
            self.corners = [[], [], [], []]

        elif self.frames == calibration_time:
            # When calibration time is done and enough corners are detected, use the data to (re)calibrate the screen
            self.calibrate(calibration_time)

        # Rotate frame according to rotation matrix set during calibration, if one exists
        if len(self.rotate_matrix) > 0:
            frame = cv2.warpAffine(frame, self.rotate_matrix, frame.shape[1::-1], flags=cv2.INTER_LINEAR)

        # Count the frames to track calibration time
        self.frames += 1
        # Set the boundaries for the screen
        min_y, max_y = max(self.min_y, 0), self.max_y
        min_x, max_x = self.min_x, max(self.max_x, 0)

        return frame[min_y:max_y, min_x:max_x]

    def measureCorners(self, frame):
        """Find the ArUco corners on a frame and store them"""
        # Convert to grayscale, invert colours
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        # Up the contrast
        cv2.convertScaleAbs(inverted, inverted, 3)
        # Detect ArUco markers
        (corners, ids, rejected) = detector.detectMarkers(inverted)
        if ids is not None:
            ids = ids.flatten()
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

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

    def calibrate(self, calibration_time):
        """Calibrate frame and rotate according to aruco corners"""
        result = []
        # Calculate the average positions of the stored inside corners
        for corner in self.corners:
            average_x = sum([x for (x, y) in corner]) / len(corner)
            average_y = sum([y for (x, y) in corner]) / len(corner)
            result.append((average_x.item(), average_y.item()))

        if DEBUG:
            # Calculate the amount of cdetected
            detected_corners = sum([len(corner) for corner in self.corners])
            frames = self.frames - 1
            confidence = min(detected_corners / 4 * 10000 // 100 / frames, 100)
            # TODO: Fix corner amount not being correct but still working for some reason
            print(
                f'Corner confidence: {confidence}% ({detected_corners} corners detected in {frames} frames)'
            )

        self.corners = result

        # Calculate the edges of the playing field according to corners calculated earlier
        self.min_x = int(min(self.corners[1][0], self.corners[2][0]))
        self.max_x = int(max(self.corners[3][0], self.corners[0][0]))
        self.min_y = int(min(self.corners[2][1], self.corners[3][1]))
        self.max_y = int(max(self.corners[1][1], self.corners[0][1]))

        # Calculate the angle of the playing field compared to the x-axis
        angle = -int(math.degrees(
            math.atan(abs(self.corners[2][1] - self.corners[3][1]) / abs(self.corners[2][0] - self.corners[3][0]))))
        # Calculate a rotation matrix according to the rotation angle
        self.rotate_matrix = cv2.getRotationMatrix2D((self.mid_x, self.mid_y), angle, 1)

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

    def ballDetection(self, frame, colour=Colour.CORK) -> tuple[tuple[int, int], int]:
        """Finds the ball, returns the coordinate, and the confidence of the found ball in amount of pixels"""
        # TODO: ff invullen
        pass

    def foosMenDetection(self, frame):
        """Looks for blue and red, and returns their outlines on the frame."""
        # cv2.convertScaleAbs(frame, frame, 2)
        blue_mask = self.colour_mask(frame, Colour.BLUE)
        red_mask = self.colour_mask(frame, Colour.RED)
        orange_mask = self.colour_mask(frame, Colour.ORANGE)
        frame = self.contour_frame(frame, blue_mask, self.foos_men_min, self.foos_men_max, Contour.BLUE)
        frame = self.contour_frame(frame, red_mask, self.foos_men_min, self.foos_men_max, Contour.RED)
        frame = self.contour_frame(frame, orange_mask, self.foos_men_min, 100000, Contour.ORANGE)

        return frame

    def contour_frame(self, frame, mask, area_min=100, area_max=1000, contour_colour=Contour.BLACK):
        """Colour all contours in a mask depending on a minimum and maximum area.
        Return the frame with contour lines."""
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area >= area_min and area <= area_max:
                x, y, w, h = cv2.boundingRect(contour)
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), contour_colour, 2)
        return frame

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

    def scale(self, frame, scaler=0.5):
        """Resize a frame according to preference in order to fit onto a laptop screen"""
        height, width, _ = frame.shape
        resize = (math.ceil(width * scaler), math.ceil(height * scaler))
        frame = cv2.resize(frame, resize)
        return frame


def testDetect():
    """Test detection functionality from a video file"""
    detection = Detection()
    # Load video file
    video = cv2.VideoCapture('data/video/shakiestcam.mp4')
    mode = Mode.NORMAL

    # Loop over all the frames
    nextFrame = True
    while nextFrame:
        nextFrame, frame = video.read()
        if nextFrame == False:
            break
        frame = detection.run(frame, mode)

        cv2.imshow('smol', frame)
        # Detect a key and select display mode for next frame accordingly
        key = cv2.waitKey(1)
        if key:
            if key == ord('q'):
                break
            elif key == ord('r'):
                mode = Mode.RED
            elif key == ord('b'):
                mode = Mode.BLUE
            elif key == ord('f'):
                mode = Mode.FUNK
            elif key == ord('n'):
                mode = Mode.NORMAL
            elif key == ord('d'):
                mode = Mode.DISCO

    video.release()
    cv2.destroyAllWindows()
