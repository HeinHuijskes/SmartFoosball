import unittest

from backend.game import Game
from hardware.mqtt_connection import Team


class ScoreKeepingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(None)
        self.mqtt = self.mqttserver(self.game, False)
        self.mqtt.send_message(Team.RED, "0")
        self.mqtt.send_message(Team.BLUE, "0")

    def test_score_increase(self):
        self.mqtt.send_message(Team.RED, "1")
        self.assertEqual(self.game.score_red, "1")

        self.mqtt.send_message(Team.BLUE, "1")
        self.assertEqual(self.game.score_blue, "1")

        self.mqtt.send_message(Team.RED, "99")
        self.assertEqual(self.game.score_red, "99")

        self.mqtt.send_message(Team.BLUE, "99")
        self.assertEqual(self.game.score_blue, "99")

    def test_score_reset(self):
        self.mqtt.send_message(Team.RED, "0")
        self.mqtt.send_message(Team.BLUE, "0")

        self.assertEqual(self.game.score_red, "0")
        self.assertEqual(self.game.score_blue, "0")


if __name__ == '__main__':
    # game = Game(None)
    # self.mqtt = self.mqttserver(game, False)
    unittest.main()
