import keyboard
class Arduino:

    def __init__(self, website, game):
        self.website = website
        self.game = game

    def run(self):
        print("hi")
        if keyboard.read_key() == "s":
            print("pressed s")
            self.game.add_goal(True)

    def key_press(self):
        if keyboard.read_key() == "s" :
            print("pressed s")
            self.game.add_goal(True)

