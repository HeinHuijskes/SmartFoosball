import time
import unittest
from unittest.mock import MagicMock, patch
from backend.game import Game, Team
from hardware.mqtt_connection import Mqttserver


class ScoreKeepingTest(unittest.TestCase):

    @patch('backend.detection.Detection.__init__', return_value=None)  # Mock the init method of Detection
    @patch('backend.detection.Detection.aruco')  # Mock any other model-dependent methods as needed
    def setUp(self, mock_detection_init, mock_aruco):
        mock_detection_init.return_value = None  # Detection's init will not run now

        self.mock_website = MagicMock()
        self.game = Game(self.mock_website)
        self.game.detector.calibrated = True  # Set any additional properties the test needs
        self.game.detector.detect = MagicMock()  # Mock detect method if it's used in tests

        self.mqtt = Mqttserver(self.game, False)
        time.sleep(1)

        self.mqtt.send_message(Team.RED, "0")
        self.mqtt.send_message(Team.BLUE, "0")

    def test_score_increase(self):
        self.assertEqual(str(self.game.score_red), "0")
        self.assertEqual(str(self.game.score_blue), "0")

        self.mqtt.send_message(Team.RED, "1")
        self.mqtt.send_message(Team.BLUE, "1")

        time.sleep(1)
        self.assertEqual(self.game.score_red, "1")
        self.assertEqual(self.game.score_blue, "1")

        self.mqtt.send_message(Team.RED, "99")
        self.mqtt.send_message(Team.BLUE, "99")

        time.sleep(1)
        self.assertEqual(self.game.score_red, "99")
        self.assertEqual(self.game.score_blue, "99")



    def test_score_reset(self):
        self.mqtt.send_message(Team.RED, "0")
        self.mqtt.send_message(Team.BLUE, "0")
        time.sleep(1)


        self.assertEqual(str(self.game.score_red), "0")
        self.assertEqual(str(self.game.score_blue), "0")


if __name__ == '__main__':
    unittest.main()
