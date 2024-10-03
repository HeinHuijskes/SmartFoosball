import cv2

# Load the image
image = cv2.imread('VideoCapture_20240916-140830.jpg')

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
parameters = cv2.aruco.DetectorParameters()

# Create the ArUco detector
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
# Detect the markers
corners, ids, rejected = detector.detectMarkers(gray)
# Print the detected markers
print("Detected markers:\n", ids)
if ids is not None:
    cv2.aruco.drawDetectedMarkers(image, corners, ids)

    # cv2.namedWindow("output", cv2.WINDOW_NORMAL)  # Create window with freedom of dimensions  # Read image
    imS = cv2.resize(image, (960, 540))  # Resize image
    cv2.imshow('Detected Markers', image)  # Show image
    cv2.waitKey(0)
