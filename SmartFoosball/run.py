from website.flask_website import *
import cv2
import argparse
from backend.game import Game


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true')
    parser.add_argument("-b", "--ball-frames", type=int)
    args = parser.parse_args()

    game = Game(None, debug=args.debug)
    if args.ball_frames:
        game.detector.ball_frames = max(args.ball_frames, 1)
    
    return game

def demo(feed):
    game = parse_arguments()
    game.run(feed)

def demo_1():
    feed = cv2.VideoCapture('data/video/cork_ball_demo.mp4')
    demo(feed)

def demo_2():
    feed = cv2.VideoCapture('data/video/white_ball_demo.mp4')
    demo(feed)
