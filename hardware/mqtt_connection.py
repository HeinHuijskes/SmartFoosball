import threading

import paho.mqtt.client as mqtt

from backend.game import Team

BROKER = '192.168.11.121'  # Example public broker, replace with your broker address
USERNAME = 'voetbal_tafel'
PASSWORD = 'voetbal_tafel'
PORT = 1883  # Default MQTT port
TOPIC_BLUE = 'sign/foosball/blue'
TOPIC_RED = 'sign/foosball/red'


class Mqttserver:
    """
    A class to represent an MQTT server.

    Attributes:
    game: An instance of the Game class.
    client:An instance of an MQTT client.
    """

    def __init__(self, game, send_only):
        """
        Initialize a new MQTT server.

        Parameters:
        game: An instance of the Game class.
        send_only(bool):A boolean which says whether the server is only sed to send messages or also to receive them(for test purposes) .
        """
        self.game = game
        # Create a new MQTT client instance
        self.client = mqtt.Client()
        # Connect to the MQTT broker
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.connect(BROKER, PORT)

        # Start the loop to process network traffic
        if not send_only:
            t1 = threading.Thread(target=self.startup, daemon=True)
            t1.start()

    def send_message(self, team, score):
        """
        Sends a message to the MQTT server

        Parameters:
        team (enum): The team which score will be updated.
        score (int): The new score of the team.
        """
        if team is Team.RED:
            self.client.publish(TOPIC_RED, str(score))
            print("sent to red")

        elif team is Team.BLUE:
            self.client.publish(TOPIC_BLUE, str(score))
            print("sent to blue")

    def on_message(self, client, userdata, message):
        """
        Handles messages from the MQTT server, a standard function from the MQTT class

        Parameters:
        userdata: not used.
        client: not used.
        message: the message object that was received from the server.
        """
        topic = message.topic
        if topic == TOPIC_RED:
            self.game.add_goal(Team.RED, message.payload.decode())
        elif topic == TOPIC_BLUE:
            self.game.add_goal(Team.BLUE, message.payload.decode())
        print(f"Message received on topic '{message.topic}': {message.payload.decode()}")

    # Callback function when connected to the broker
    def on_connect(self, client, userdata, flags, rc):
        """
        Triggers when connected to the MQTT server, a standard function from the MQTT class

        Parameters:
        userdata: not used.
        client: the MQTT client that connects to the server.
        flags: not used.
        rc: result code, says whether connecting was successful.
        """
        print(f"Connected with result code {rc}")
        client.subscribe(TOPIC_RED)  # Subscribe to the topic
        client.subscribe(TOPIC_BLUE)  # Subscribe to the topic
        # self.client.publish(TOPIC_RED, str(4))

    def startup(self):
        """
        Assigns the callback functions to the client object
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

