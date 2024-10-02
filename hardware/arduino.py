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
        self.reset = False
        self.thread = Thread(target=self.loop, daemon=True)
        self.lock = Lock()
        self.thread.start()

    def loop(self):
        while True:
            if self.serialConnection.in_waiting:
                self.lock.acquire()

            line = self.get_line()
            if line == ('Goal red'):
                self.goal = Team.RED
            elif line == ('Goal blue'):
                self.goal = Team.BLUE
            elif line == "reset":
                self.reset = True

                self.lock.release()

    def get_goal_or_reset(self):
        self.lock.acquire()
        goal = self.goal
        self.goal = None
        reset = self.reset
        self.reset = False
        self.lock.release()

        return goal, reset

    def get_line(self):
        line = self.serialConnection.readline()
        line = line.decode('ascii').strip()
        return line


if __name__ == '__main__':
    pass
