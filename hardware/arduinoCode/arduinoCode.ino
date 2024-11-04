#include <OneButton.h>
#include "FastLED.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

#define BUTTON_PIN 26
#define DELAY 2000
#define LED_PIN_BLUE 2
#define LED_PIN_TOP 5
#define LED_PIN_RED 13
#define NUM_LEDS_BLUE 100
#define NUM_LEDS_RED 100
#define NUM_LEDS_TOP 37

//Sensor
int sensorPinBlue = 35;  //define analog pin 2
int sensorPinRed = 34;   //define analog pin 3
int counterBlue = 0;
int counterRed = 0;
int tresholdBlue = 850;
int tresholdRed = 700;
OneButton resetButton;

//LEDs
uint8_t gHue = 0;
CRGB ledsBlue[NUM_LEDS_BLUE];  //Initializes an array of CRGB objects(individual LEDs)
CRGB ledsRed[NUM_LEDS_RED];    //Initializes an array of CRGB objects(individual LEDs)
CRGB ledsTop[NUM_LEDS_TOP];    //Initializes an array of CRGB objects(individual LEDs)

TaskHandle_t Task1;

//basic colors
CRGB red = CRGB(128, 0, 0);
CRGB blue = CRGB(0, 0, 48);
CRGB white = CRGB(255, 128, 100);
CRGB black = CRGB(0, 0, 0);
CRGB green = CRGB(0, 48, 0);
CRGB pink = CRGB(64, 0, 16);

//wifi connection
const char* ssid = "IoT Cyberlab Zi2070 experiments";
const char* password = "Kr83AkM3n03@";
WiFiClientSecure client;

//MQTT connection
const char* mqtt_server = "192.168.11.121";
const char* mqtt_user = "voetbal_tafel";
const char* mqtt_pass = "voetbal_tafel";
const char* mqtt_topic_red = "sign/foosball/red";    // MQTT topic to publish messages
const char* mqtt_topic_blue = "sign/foosball/blue";  // MQTT topic to publish messages
const char* mqtt_topic_calibrate = "sign/foosball/calibrate"; // MQTT topic for calibrating
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

//variables
int score_red = 0;
int score_blue = 0;

/*
This function is the standard setup function, it is called on startup by the ESP32.

Output:
  There is no return value, it ensures that all the pins are initialized properly and that the wifi and MQTT server are connected.
*/
void setup() {
  Serial.begin(9600);
  resetButton = OneButton(BUTTON_PIN, true, true);
  resetButton.attachPress(handleReset);

  pinMode(LED_PIN_BLUE, OUTPUT);
  pinMode(LED_PIN_TOP, OUTPUT);
  pinMode(LED_PIN_RED, OUTPUT);
  LEDS.addLeds<WS2812B, LED_PIN_BLUE, GRB>(ledsBlue, NUM_LEDS_BLUE);
  LEDS.addLeds<WS2812B, LED_PIN_RED, GRB>(ledsRed, NUM_LEDS_RED);
  LEDS.addLeds<WS2812B, LED_PIN_TOP, GRB>(ledsTop, NUM_LEDS_TOP);
  LEDS.setBrightness(255);

  connect_wifi();
  mqtt_client.setServer(mqtt_server, 1883);  // Port 1883 for non-SSL MQTT
  mqtt_client.setCallback(callback);

  reconnect();
  mqtt_client.publish(mqtt_topic_red, String(score_red).c_str());
  mqtt_client.publish(mqtt_topic_blue, String(score_blue).c_str());

  waveUp(white, white, white);
  tresholdBlue = getTreshold(sensorPinBlue);
  tresholdRed = getTreshold(sensorPinRed);
  waveDown(blue, red, 0);

  Serial.println("start");
  // calibrateAruco();
}

/*
This function is the standard loop function, it is continuously called by the ESP32.

Output:
  There is no return value, it calls all the functions when they need to be called and makes sure the MQTT server is connected.
*/
void loop() {
  // Reconnect if not connected
  if (!mqtt_client.connected()) {
    reconnect();
  }

  mqtt_client.loop();  // Ensure MQTT client stays connected
  resetButton.tick();
  checkGoal(sensorPinBlue, &counterBlue, "blue", tresholdBlue);
  checkGoal(sensorPinRed, &counterRed, "red", tresholdRed);
}


/*
This function checks whether a goal has been made.
It does this by measuring whether the sensor output is higher than the threshold for a few measurements in a row.

Input:
  int sensorPin: the pin to which the sensor is connected
  int* counter: the counter that belongs to the sensorPin
  String team: the team that might make a goal
  int treshold: the threshold belonging to the sensorPin

Output:
  There is no return value, but the ESP32 will send a message to the MQTT server and activate the LEDs in case a goal is detected.
*/
void checkGoal(int sensorPin, int* counter, String team, int treshold) {
  int value = analogRead(sensorPin);
  delay(1);

  if (value >= treshold) {
    (*counter)++;

    if (*counter >= 12) {
      Serial.println("Goal " + team);
      if (team == "red") {
        score_red++;
        mqtt_client.publish(mqtt_topic_red, String(score_red).c_str());

        xTaskCreatePinnedToCore(
          goalRedLights,     /* Function to implement the task */
          "Red goal lights", /* Name of the task */
          100000,            /* Stack size in words */
          (void*)&red,       /* Task input parameter */
          0,                 /* Priority of the task */
          &Task1,            /* Task handle. */
          0);                /* Core where the task should run */

      } else {
        score_blue++;
        mqtt_client.publish(mqtt_topic_blue, String(score_blue).c_str());

        xTaskCreatePinnedToCore(
          goalBlueLights,     /* Function to implement the task */
          "Blue goal lights", /* Name of the task */
          100000,             /* Stack size in words */
          (void*)&blue,       /* Task input parameter */
          0,                  /* Priority of the task */
          &Task1,             /* Task handle. */
          0);                 /* Core where the task should run */
      }
      *counter = 0;
      Serial.println(value);
      delay(DELAY);

      while (analogRead(sensorPin >= treshold)) {
        delay(100);
      }
    }
  } else {
    *counter = 0;
  }
}

/*
This function sets the threshold above which the ESP32 will detect a goal.
It does this by taking the average input of 10 measurements and multiplying by 1.1 so random spikes do not trigger a goal.

Input:
  int sensorPin: the pin of which the program will take the output

Output:
  There is no return value, but the threshold of the given pin will be set to a good value so goals will be detected.
*/
int getTreshold(int sensorPin) {
  int iterations = 10;
  int total = 0;


  for (int i = 0; i < iterations; i++) {
    total += analogRead(sensorPin);
  }

  int treshold = (total / iterations) * 1.1;

  Serial.print("treshold is: ");
  Serial.println(treshold);

  return treshold;
}

/*
This function ensures the ESP32 is connected to the MQTT server.

Output:
  There is no return value, the ESP32 will be connected to the MQTT server.
*/
void reconnect() {
  // Loop until the client is connected
  while (!mqtt_client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Try to connect using client ID, username, and password
    if (mqtt_client.connect("ESP32Client", mqtt_user, mqtt_pass)) {
      Serial.println("connected");
      mqtt_client.subscribe("sign/foosball/calibrate");

    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}


/*
This function connects the ESP32 with the wifi.

Output:
  There is no return value, the ESP32 will be connected to the wifi.
*/
void connect_wifi() {
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  client.setInsecure();

  if (client.connect("your-server.com", 443)) {
    Serial.println("Connected without SSL validation!");
  } else {
    Serial.println("Connection failed.");
  }
}

/*
This function handles incoming messages from the MQTT server.
It runs automatically when the server publishes something new

Input:
  char* topic: the topic the message is from
  byte* message: the message that is received
  unsigned int length: the length of the received message

Output:
  There is no return value, but the threshold of the given pin will be set to a good value so goals will be detected.
*/
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  // Feel free to add more if statements to control more GPIOs with MQTT

  if (String(topic) == "sign/foosball/calibrate") {
    if (messageTemp == "calibrate") {
      calibrateAruco();
    } else if (messageTemp == "stop calibrating") {
      stopCalibrating();
    }
  }
}


/*
This function resets the score to 0-0 and sets a new threshold for the goal sensors.

Output:
  There is no return value, but the score will be 0-0.
*/
void handleReset() {
  Serial.println("reset");
  score_blue = 0;
  score_red = 0;
  mqtt_client.publish(mqtt_topic_red, String(score_red).c_str());
  mqtt_client.publish(mqtt_topic_blue, String(score_blue).c_str());

  fillSolid(black, ledsTop, NUM_LEDS_TOP);
  waveUp(white, white, white);
  tresholdBlue = getTreshold(sensorPinBlue);
  tresholdRed = getTreshold(sensorPinRed);
  waveDown(blue, red, 0);

  calibrateAruco();
  delay(2000);
  stopCalibrating();
}