from flask import Flask, render_template, Response
# from picamera2 import Picamera2
import cv2
import threading
import time
import queue
from flask import request

app = Flask(__name__)

# Initialize the camera and frame buffer
camera = None
camera_init = False
frames = []
current_frame = None
start_time = time.time()
passed = False

MAX_BUFFER_SIZE = 10  # in seconds


def initialize_camera():
    global camera
    if not camera:
        try:
            camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            # camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
            # camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
            print("Camera initialized successfully.")
            camera_init = True
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            camera_init = False


def initialize_queue():
    passed = False
    start_time = time.time()
    while not passed:
        ret, frame = camera.read()

        if ret:
            # frame_buffer.put(frame)
            # frame_time.append(time.time())
            frames.append((frame, time.time()))

        # TODO put back to 30
        if time.time() - start_time > MAX_BUFFER_SIZE:
            passed = True
            # print(frame_buffer.qsize())
            print("queue initialized")


def capture_frames():
    global current_frame, frames
    while True:
        try:
            ret, frame = camera.read()
            # cv2.imshow('preview',frame)

            if ret:
                current_frame = frame
                # frame_buffer.put(frame)
                # frame_time.append(time.time())
            frames.append((frame, time.time()))

            # frame_buffer.get()
        except Exception as e:
            print(f"Exception in capture_frames: {e}")


def generate_frames():
    global current_frame
    while True:
        ret, jpeg = cv2.imencode('.jpg', current_frame)
        if ret:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   jpeg.tobytes() + b'\r\n')


def get_video(seconds):
    global frames
    timestamp = time.time()
    # dupe list
    frames_copy = []
    frames_copy.extend(frames)

    #  find where the start of the playback is
    for i in range(len(frames_copy)):
        if timestamp - frames_copy[i][1] < seconds:
            # copy the rest of the list
            return frames_copy[i:]


def delayed_frames(seconds):
    # global frame_count
    video = get_video(seconds)  # get cropped video
    frame_count = 0  # in this replay, on which frame are you
    fps = seconds / len(video)
    start_time = time.perf_counter()

    while True:
        if time.perf_counter() - start_time > fps:
            start_time = time.perf_counter()
            # ret, jpeg = cv2.imencode('.jpg', frame_buffer.get())
            print(frame_count)
            ret, jpeg = cv2.imencode('.jpg', video[frame_count][0])
            frame_count += 1

            # frame_time.remove(frame_time[0])

            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n')


def check_queue():
    global frames
    while True:
        while time.time() - frames[0][1] > MAX_BUFFER_SIZE:
            # frame_buffer.get()
            frames.remove(frames[0])
            # print("frame removed")
        time.sleep(0.5)
        # print("running")


playback = 0


@app.route('/', methods=['GET', 'POST'])
def index():
    global playback
    if request.method == 'POST':
        playback = request.args.get('playback', default=15, type=int)
        if playback == 0:
            return render_template('index.html', link='/video_feed', )
        else:
            return render_template('index.html', link='/delayed_video_feed', )
    return render_template('index.html', link='/video_feed')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/delayed_video_feed')
def delayed_video_feed():
    global playback
    return Response(delayed_frames(playback), mimetype='multipart/x-mixed-replace; boundary=frame')

