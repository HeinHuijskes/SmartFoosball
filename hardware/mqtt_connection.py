import threading
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
    def __init__(self, game, send_only):
        self.game = game
        # Create a new MQTT client instance
        self.client = mqtt.Client()
        # Connect to the MQTT broker
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.connect(BROKER, PORT)
        # Assign the callback functions

        # Start the loop to process network traffic
        if not send_only:
            t1 = threading.Thread(target=self.startup, daemon=True)
            t1.start()

    def send_message(self, team, score):
        if team is Team.RED:
            self.client.publish(TOPIC_RED, str(score))
            print("sent to red")

        elif team is Team.BLUE:
            self.client.publish(TOPIC_BLUE, str(score))
            print("sent to blue")

        # Disconnect from the broker
        # self.client.disconnect()

    def on_message(self, client, userdata, message):
        topic = message.topic
        if topic == TOPIC_RED:
            self.game.add_goal(Team.RED, message.payload.decode())
        elif topic == TOPIC_BLUE:
            self.game.add_goal(Team.BLUE, message.payload.decode())
        print(f"Message received on topic '{message.topic}': {message.payload.decode()}")

    # Callback function when connected to the broker
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(TOPIC_RED)  # Subscribe to the topic
        client.subscribe(TOPIC_BLUE)  # Subscribe to the topic
        # self.client.publish(TOPIC_RED, str(4))

    def startup(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

# while True:
#     mqtt = Mqttserver()
#     mqtt.send_message(Team.RED,"2")
