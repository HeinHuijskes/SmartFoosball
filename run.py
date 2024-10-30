from website.flask_website import *
import cv2


game = Game(None)
feed = cv2.VideoCapture('data/video/best yet.mp4')
# feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# print(feed)
# print(feed.read())
# while True:
#     nextFrame, frame = feed.read()
#     game.showFrame(frame)
game.run(feed)
# Website().run(0)
