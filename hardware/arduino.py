from threading import Thread, Lock

import serial
from enum import Enum


class Team(Enum):
    RED = 1
    BLUE = 2


class Arduino:
    def __init__(self, com_port='COM3'):
        self.serialConnection = serial.Serial(com_port, 9600)
        self.goal = None
        self.thread = Thread(target=self.loop, daemon=True)
        self.lock = Lock()
        self.thread.start()

    def loop(self):
        while True:
            self.lock.acquire()

            line = self.get_line()
            if line == ('Goal red'):
                self.goal = Team.RED
            elif line == ('Goal blue'):
                self.goal = Team.BLUE

            self.lock.release()

    def get_goal(self):
        self.lock.acquire()
        goal = self.goal
        self.goal = None
        self.lock.release()

        return goal

    def get_line(self):
        line = self.serialConnection.readline()
        line = line.decode('ascii').strip()
        return line


if __name__ == '__main__':
    pass
