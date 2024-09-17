#!/usr/bin/env python

'''
Welcome to the ArUco Marker Detector!

This program:
  - Detects ArUco markers using OpenCV and Python
'''

from __future__ import print_function  # Python 2/3 compatibility
import cv2  # Import the OpenCV library
import numpy as np  # Import Numpy library

# Project: ArUco Marker Detector
# Date created: 12/18/2021
# Python version: 3.8
# Reference: https://www.pyimagesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

desired_aruco_dictionary = "DICT_ARUCO_ORIGINAL"


# The different ArUco dictionaries built into the OpenCV library.


def main():
    """
    Main method of the program.
    """

    # Load the ArUco dictionary
    print("[INFO] detecting '{}' markers...".format(
        desired_aruco_dictionary))
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Start the video stream
    # cap = cv2.VideoCapture('IMG_6903.MOV')
    cap = cv2.VideoCapture(0)


    while True:

        # Capture frame-by-frame
        # This method returns True/False as well
        # as the video frame.
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)

        display_frame = frame

        # Detect ArUco markers in the video frame
        (corners, ids, rejected) = detector.detectMarkers(gray)

        # Check that at least one ArUco marker was detected
        if len(corners) > 0:
            # Flatten the ArUco IDs list
            ids = ids.flatten()

            cv2.aruco.drawDetectedMarkers(display_frame, corners, ids)

        # Display the resulting frame
        # cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('frame', 324, 576)
        cv2.imshow('frame', display_frame)

        # If "q" is pressed on the keyboard,
        # exit this loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close down the video stream
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print(__doc__)
    main()
