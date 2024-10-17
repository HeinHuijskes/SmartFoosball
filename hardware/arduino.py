import time
import serial
import keyboard
from enum import Enum
import keyboard
import serial.tools.list_ports


# arduino = False

class Team(Enum):
    RED = 1
    BLUE = 2



class Arduino:

    def __init__(self, website, game, com_port='COM3'):
        self.website = website
        self.game = game
        self.arduino = False
        # self.lock = Lock()

        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            # print(p)
            if "USB-SERIAL" in p.description:
                # pass
                self.arduino = True
                self.serialConnection = serial.Serial(p.name, 9600)

        if not self.arduino:
            print("Arduino not connected")


    def run(self):
        while True:
            if self.arduino:
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
            else:
                if keyboard.read_key() == "l":
                    print("pressed l")
                    self.game.add_goal(True)
                    time.sleep(0.1)
                if keyboard.read_key() == "r":
                    print("pressed r")
                    self.game.add_goal(False)
                    time.sleep(0.1)

    def key_press(self):
        if keyboard.read_key() == "s":
            print("pressed s")
            self.game.add_goal(True)

    def get_line(self):
        if self.arduino:
            line = self.serialConnection.readline()
            line = line.decode('ascii').strip()
            return line