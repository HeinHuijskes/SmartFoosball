import numpy as np

CONTOUR = dict(
    RED = (0, 0, 255),
    GREEN = (0, 255, 0),
    BLUE = (255, 0, 0),
    BLACK = (0, 0, 0)
)

MODE = dict(
    NORMAL = 'NORMAL',
    RED = 'RED',
    BLUE = 'BLUE',
    FUNK = 'FUNK',
)

RED = [
    np.array([150, 60, 0], np.uint8), # Lower
    np.array([200, 255, 255], np.uint8), # Upper
]
GREEN = []
BLUE = [
    np.array([100, 125, 0], np.uint8), # Lower
    np.array([150, 255, 255], np.uint8), # Upper
]
WHITE = [
    np.array([0, 0, 220], np.uint8), # Lower
    np.array([255, 25, 255], np.uint8), # Upper
]
BLACK = []
CORK = []