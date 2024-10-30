import unittest

from backend.game import Game
from hardware.mqtt_connection import Mqttserver, Team


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        mqtt.send_message(Team.RED, "0")
        mqtt.send_message(Team.BLUE, "0")

    def test_score_increase(self):
        mqtt.send_message(Team.RED, "1")
        self.assertEqual(game.score_red, "1")

        mqtt.send_message(Team.BLUE, "1")
        self.assertEqual(game.score_blue, "1")

        mqtt.send_message(Team.RED, "99")
        self.assertEqual(game.score_red, "99")

        mqtt.send_message(Team.BLUE, "99")
        self.assertEqual(game.score_blue, "99")

    def test_score_reset(self):
        mqtt.send_message(Team.RED, "0")
        mqtt.send_message(Team.BLUE, "0")

        self.assertEqual(game.score_red, "0")
        self.assertEqual(game.score_blue, "0")


if __name__ == '__main__':
    game = Game(None)
    mqtt = Mqttserver(game, False)
    unittest.main()
