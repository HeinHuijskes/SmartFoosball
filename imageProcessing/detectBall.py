import cv2
import math
import numpy as np
import time

RED = [
    np.array([150, 25, 0], np.uint8), # Lower
    np.array([200, 255, 255], np.uint8), # Upper
]
GREEN = []
BLUE = [
    np.array([100, 100, 0], np.uint8), # Lower
    np.array([150, 255, 255], np.uint8), # Upper
]
WHITE = [
    np.array([0, 0, 220], np.uint8), # Lower
    np.array([255, 25, 255], np.uint8), # Upper
]
BLACK = []
CORK = []

FILTER = WHITE

def contour_frame(frame, mask, area_size = 400):
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > area_size and area < area_size*10:
            x, y, w, h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame

def colour_mask(colour, frame):
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsvFrame, colour[0], colour[1])
    kernel = np.ones((5, 5), "uint8")
    mask = cv2.dilate(mask, kernel)
    
    # mask = cv2.inRange(frame, 200, 255)
    frame = cv2.bitwise_and(frame, frame, mask = mask)
    frame = contour_frame(frame, mask)

    return frame

def crop(frame, scale):
    height, width, _ = frame.shape
    min_x, max_x = math.ceil(width*scale*0.5), math.ceil(width - width*scale*0.5)
    min_y, max_y = math.ceil(height*scale*0.5), math.ceil(height - height*scale*0.5)
    return frame[min_y:max_y, min_x:max_x]

def detect():
    video = cv2.VideoCapture('data/video/latest - Trim.mp4')

    nextFrame = True
    framecounter = 0
    frame_array = []
    while nextFrame:
        nextFrame, frame = video.read()
        
        # cv2.imshow('big', frame)
        # cv2.waitKey(0)
        
        if nextFrame == False:
            break
        frame = colour_mask(FILTER, frame)
        # cv2.imshow('colour', frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # break

        height, width, _ = frame.shape
        scaler = 0.5
        resize = (math.ceil(width*scaler), math.ceil(height*scaler))
        frame = cv2.resize(frame, resize)
        frame = crop(frame, 0.25)
        frame_array.append(frame)
        cv2.imshow('smol', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()

    out = cv2.VideoWriter('data/video/output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 25, resize, False)
    for frame in frame_array:
        out.write(frame)
    out.release()