import time

import serial

import keyboard
class Arduino:

    def __init__(self, website, game):
        self.website = website
        self.game = game

    def run(self):
        while True:
            time.sleep(5)
            print("added goal")
            self.game.add_goal(True)
            time.sleep(0.1)

    def key_press(self):
        if keyboard.read_key() == "s" :
            print("pressed s")
            self.game.add_goal(True)
