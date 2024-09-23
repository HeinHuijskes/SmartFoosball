import cv2

class Camera:
    def __init__(self, camera_number=0):
        self.camera = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)

    def get_frame(self):
        ret, frame = self.camera.read()
        return frame
