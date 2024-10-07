import time
import serial
import keyboard
from enum import Enum
import keyboard

arduino = False

class Team(Enum):
    RED = 1
    BLUE = 2


class Arduino:

    def __init__(self, website, game, com_port='COM3'):
        self.website = website
        self.game = game
        if arduino:
            self.serialConnection = serial.Serial(com_port, 9600)
        # self.lock = Lock()

    def run(self):
        while True:
            if arduino:
                if self.serialConnection.in_waiting:
                    line = self.get_line()

                    # red is left
                    if line == 'Goal red':
                        print("red goal")
                        self.game.add_goal(True)
                        time.sleep(0.1)
                    elif line == 'Goal blue':
                        print("blue goal")
                        self.game.add_goal(False)
                        time.sleep(0.1)
                    elif line == "reset":
                        self.game.reset_game()

    def key_press(self):
        if keyboard.read_key() == "s":
            print("pressed s")
            self.game.add_goal(True)

    def get_line(self):
        if arduino:
            line = self.serialConnection.readline()
            line = line.decode('ascii').strip()
            return line