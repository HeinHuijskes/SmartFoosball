from enum import Enum

import paho.mqtt.client as mqtt


class Team(Enum):
    RED = 1
    BLUE = 2


BROKER = '192.168.11.121'  # Example public broker, replace with your broker address
USERNAME = 'voetbal_tafel'
PASSWORD = 'voetbal_tafel'
PORT = 1883  # Default MQTT port
TOPIC_BLUE = 'sign/foosball/blue'
TOPIC_RED = 'sign/foosball/red'


class Mqttserver:
    def __init__(self):
        # Create a new MQTT client instance
        self.client = mqtt.Client()
        # Connect to the MQTT broker
        self.client.username_pw_set(USERNAME, PASSWORD)

    def send_message(self, team, score):
        self.client.connect(BROKER, PORT)

        if team is Team.RED:
            self.client.publish(TOPIC_RED, str(score))
            print("sent to red")

        elif team is Team.BLUE:
            self.client.publish(TOPIC_BLUE, str(score))
            print("sent to blue")

        # Disconnect from the broker
        self.client.disconnect()
