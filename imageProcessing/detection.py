import cv2
import math
import numpy as np
from imageProcessing.misc import MODE, CONTOUR
from imageProcessing.misc import RED, GREEN, BLUE, WHITE, BLACK, CORK

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

class Detection():
    def __init__(self):
        self.foos_men_min = 250
        self.foos_men_max = 1500
        self.corners = [[], [], [], []]
        self.frames = 0

    def run(self, frame, mode = MODE['NORMAL']):

        frame = self.scale(frame, 0.5)
        frame = self.aruco(frame)

        frame = self.applyMode(mode, frame)
        return self.foosMenDetection(frame)
    
    def applyMode(self, mode, frame):
        if mode == MODE['BLUE']:
            mask = self.colour_mask(frame, BLUE)
        elif mode == MODE['RED']:
            mask = self.colour_mask(frame, RED)
        elif mode == MODE['FUNK']:
            red_mask = self.colour_mask(frame, RED)
            blue_mask = self.colour_mask(frame, BLUE)
            mask = red_mask | blue_mask
        else:
            return frame

        return cv2.bitwise_and(frame, frame, mask = mask)

    def aruco(self, frame, calibration_time = 30):
        '''Detects aruco, returns the bounding box of the foosball table'''

        frame = cv2.flip(frame, 1)
        if self.frames == 0:
            height, width, _ = frame.shape
            self.min_x = 0
            self.max_x = width
            self.min_y = 0
            self.max_y = height

        elif self.frames < calibration_time: # TODO: Make in line with measured FPS
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            inverted = cv2.bitwise_not(gray)
            cv2.convertScaleAbs(inverted, inverted, 3)
            (corners, ids, rejected) = detector.detectMarkers(inverted)
            ids = ids.flatten()
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for (marker, id) in zip(corners, ids): 
                corner = marker.reshape((4, 2))
                (tl, tr, br, bl) = corner
                cx = (tl[0] + br[0]) / 2
                cy = (tl[1] + br[1]) / 2
                if len(corners[0][0]) == 4:
                    self.corners[id].append((cx, cy))
        
        elif self.frames == calibration_time:
            result = []
            for corner in self.corners:
                average_x = sum([x for (x,y) in corner]) / len(corner)
                average_y = sum([y for (x,y) in corner]) / len(corner)
                result.append((average_x.item(), average_y.item()))
            self.corners = result
            print(f'Corner confidence: {len(corner)*10000//100/calibration_time}% ({len(corner)} corners detected in {calibration_time} frames)')
            self.min_x = int(self.corners[1][0])
            self.max_x = int(self.corners[2][0])
            self.min_y = int(self.corners[1][1])
            self.max_y = int(self.corners[2][1])
            print(frame.shape)
            print(self.corners)
        
        elif self.frames > 1000:
            self.frames = 1

        frame = frame[max(self.min_y,0):self.max_y, self.min_x:max(self.max_x,0)]
        self.frames += 1

        return frame
    
    def ballDetection(self, frame, colour = CORK) -> tuple[tuple[int, int], int]:
        '''Finds the ball, returns the coordinate, and the confidence of the found ball in amount of pixels'''
        pass

    def foosMenDetection(self, frame):
        '''Looks for blue and red, and returns their outlines on the frame.'''
        blue_mask = self.colour_mask(frame, BLUE)
        red_mask = self.colour_mask(frame, RED)
        frame = self.contour_frame(frame, blue_mask, self.foos_men_min, self.foos_men_max, CONTOUR['RED'])
        frame = self.contour_frame(frame, red_mask, self.foos_men_min, self.foos_men_max, CONTOUR['BLUE'])

        return frame

    def crop(self, frame, scale):
        '''Crops the frame to a correct size, returns the cropped frame'''
        height, width, _ = frame.shape
        min_x, max_x = math.ceil(width*scale*0.5), math.ceil(width - width*scale*0.5)
        min_y, max_y = math.ceil(height*scale*0.5), math.ceil(height - height*scale*0.5)
        return frame[min_y:max_y, min_x:max_x]

    def contour_frame(self, frame, mask, area_min = 100, area_max = 1000, contour_colour = CONTOUR['BLACK']):
        '''Colour all contours in a mask depending on a minimum and maximum area. Returns the frame with contour lines.'''
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area >= area_min and area <= area_max:
                x, y, w, h = cv2.boundingRect(contour)
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), contour_colour, 2)
        return frame

    def colour_mask(self, frame, colour):
        '''Obtain the mask of colours in a frame.'''
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsvFrame, colour[0], colour[1])
        kernel = np.ones((5, 5), "uint8")
        mask = cv2.dilate(mask, kernel)
        
        # frame = self.contour_frame(frame, mask)

        return mask
    
    def scale(self, frame, scaler):
        height, width, _ = frame.shape
        scaler = 0.5
        resize = (math.ceil(width*scaler), math.ceil(height*scaler))
        frame = cv2.resize(frame, resize)
        return frame


def testDetect():
    detection = Detection()
    video = cv2.VideoCapture('data/video/latest - Trim.mp4')
    mode = 'FULL'

    nextFrame = True
    while nextFrame:
        nextFrame, frame = video.read()
        if nextFrame == False:
            break
        frame = detection.run(frame, mode)

        cv2.imshow('smol', frame)
        key = cv2.waitKey(1)
        if key:
            if key == ord('q'):
                break
            elif key == ord('r'):
                mode = 'RED'
            elif key == ord('b'):
                mode = 'BLUE'
            elif key == ord('f'):
                mode = 'FUNK'
            elif key == ord('n'):
                mode = 'NORMAL'

    video.release()
    cv2.destroyAllWindows()