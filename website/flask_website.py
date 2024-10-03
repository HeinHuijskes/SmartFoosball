from flask import Flask, render_template, Response, jsonify
import cv2
from flask import request
import threading

from game.game import Game
from hardware.hardware import *
from hardware.arduino import Arduino

global app


class Website:

        def __init__(self):
            # Initialize the camera and frame buffer
            self.app = Flask(__name__)
            self.add_routes()
            self.camera = None
            self.camera_id = 0
            self.game = Game(self)
            self.scoreL = 0
            self.scoreR = 0
            self.arduino = Arduino(self, self.game)
            self.max_speed = 0

        def run(self, camera_id):
            self.camera_id = camera_id
            self.camera = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            print("Camera initialized successfully.")
            #start arduino class
            t1 = threading.Thread(target=self.arduino.run,)
            t1.start()
            self.app.run(debug=True, threaded=True, use_reloader=False)


        def generate_frames2(self, frame):
            ret, jpeg = cv2.imencode('.jpg', frame)
            cv2.imwrite("frame.jpg", jpeg)
            if frame is None or frame.size == 0:
                print("frame error")
            if not ret:
                print("ret not true")
            if ret:
                frame = jpeg.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                frame + b'\r\n')
            self.camera.release()
            cv2.destroyAllWindows()

        def add_goal(self, Left):
            "If Left is true, one goal will be added to the score of the left goal, else 1 will be added to the right goal"
            if Left:
                self.scoreL = self.scoreL + 1
            else: self.scoreR = self.scoreR + 1

        def add_routes(self):
            @self.app.route('/', methods=['GET', 'POST'])
            def index():
                    global playback
                    if request.method == 'POST':
                        playback = request.args.get('playback', default=15, type=int)
                        if playback == 0:
                            return render_template('feedpage.html', link='/video_feed', )
                        else:
                            return render_template('index.html', link='/video_feed', )
                    return render_template('index.html', link='/video_feed')

            @self.app.route('/video_feed')
            def video_feed():
                return Response(self.game.run_camera(self.camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

            @self.app.route('/delayed_video_feed')
            def delayed_video_feed():
                print("error")
                return Response(self.game.buffer_frames(),
                                mimetype='multipart/x-mixed-replace; boundary=frame')

            @self.app.route('/feedpage.html')
            def feedpage():
                # self.arduino.run()
                return render_template('feedpage.html', scoreL = self.scoreL, scoreR= self.scoreR, max_speed = self.max_speed)

            @self.app.route('/index.html')
            def indexhtml():
                return render_template('index.html')

            @self.app.route('/css/styles.css')
            def cssstyles():
                return render_template('css/styles.css')

            @self.app.route('/score')
            def score():
                return render_template('feedpage.html', scoreL = self.scoreL, scoreR= self.scoreR)

            @self.app.route('/update_score')
            def update_score():
                return jsonify(scoreL = self.scoreL, scoreR= self.scoreR)

            @self.app.route('/update_speed')
            def update_speed():
                self.max_speed = self.game.get_max_speed()
                return jsonify(max_speed=self.max_speed)

