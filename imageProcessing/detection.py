import cv2
import math
import numpy as np
from imageProcessing.misc import MODE, CONTOUR
from imageProcessing.misc import RED, GREEN, BLUE, WHITE, BLACK, CORK

class Detection():
    def __init__(self):
        self.foos_men_min = 250
        self.foos_men_max = 1500

    def run(self, frame, mode = MODE['NORMAL']):

        frame = self.scale(frame, 0.5)

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

    def aruco(self, frame) -> list[tuple[int, int]]:
        '''Detects aruco, returns the bounding box of the foosball table'''
        pass
    
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