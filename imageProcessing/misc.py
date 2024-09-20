import numpy as np
from enum import Enum


class Colour:
    """HSV Colour ranges for detecting different colours"""
    RED = [
        np.array([0, 120, 0], np.uint8),  # Lower
        np.array([15, 255, 255], np.uint8),  # Upper
    ]
    GREEN = []
    BLUE = [
        np.array([100, 125, 0], np.uint8),  # Lower
        np.array([150, 255, 255], np.uint8),  # Upper
    ]
    WHITE = [
        np.array([0, 0, 220], np.uint8),  # Lower
        np.array([255, 25, 255], np.uint8),  # Upper
    ]
    BLACK = []
    CORK = []
    ORANGE = [
        np.array([20, 50, 50], np.uint8),  # Lower
        np.array([60, 255, 255], np.uint8),  # Upper
    ]


class Contour:
    """BGR Colour values for drawing with colours"""
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    ORANGE = (0, 165, 255)
    BLACK = (0, 0, 0)


class Mode(Enum):
    """Display modes"""
    NORMAL = 'NORMAL'
    RED = 'RED'
    BLUE = 'BLUE'
    FUNK = 'FUNK'
    DISCO = 'DISCO'
    ORANGE = 'ORANGE'
