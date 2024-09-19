import cv2

camera = None


def init_camera():
    global camera
    if not camera:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("Camera initialized successfully.")

        while True:
            ret, frame = camera.read()
            if ret:
                cv2.imshow("video", frame)

            # Wait for 1ms and check if the user pressed 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == '__main__':
    try:
        init_camera()
    finally:
        if camera:
            camera.release()
            cv2.destroyAllWindows()
