#include <OneButton.h>
#include "FastLED.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

#define BUTTON_PIN 26
#define DELAY 2000
#define DATA_PIN 2
#define NUM_LEDS 60

//Sensor
int sensorPinBlue = 34; //define analog pin 2
int sensorPinRed = 35; //define analog pin 3
// int valueBlue = 0;
int counterBlue = 0;
int counterRed = 0;
int blueGoals = 0;
int tresholdBlue = 850;
int tresholdRed = 700;
OneButton resetButton;

//LEDs
uint8_t gHue = 0;
CRGB leds[NUM_LEDS];
TaskHandle_t Task1;

//wifi connection
const char* ssid = "IoT Cyberlab Zi2070 experiments";
const char* password = "Kr83AkM3n03@";
WiFiClientSecure client;

//MQTT connection
const char* mqtt_server = "192.168.11.121";
const char* mqtt_user = "voetbal_tafel";
const char* mqtt_pass = "voetbal_tafel";
const char* mqtt_topic_red = "sign/foosball/red";          // MQTT topic to publish messages
const char* mqtt_topic_blue = "sign/foosball/blue";          // MQTT topic to publish messages
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

//variables
int score_red = 0;
int score_blue = 0;


void setup() {
	Serial.begin(9600);
  resetButton = OneButton(BUTTON_PIN, true, true);
  resetButton.attachPress(handleReset);

  tresholdBlue = getTreshold(sensorPinBlue);
  tresholdRed = getTreshold(sensorPinRed);

  Serial.print("Blue treshold is: ");
  Serial.println(tresholdBlue);
  Serial.print("Red treshold is: ");
  Serial.println(tresholdRed);

  pinMode(DATA_PIN, OUTPUT);
  LEDS.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  LEDS.setBrightness(64);

  xTaskCreatePinnedToCore(
      lightLoop, /* Function to implement the task */
      "Lights", /* Name of the task */
      10000,  /* Stack size in words */
      NULL,  /* Task input parameter */
      0,  /* Priority of the task */
      &Task1,  /* Task handle. */
      0); /* Core where the task should run */




  connect_wifi();
  mqtt_client.setServer(mqtt_server, 1883);  // Port 1883 for non-SSL MQTT

  Serial.println("start");

}

void loop() {
  // Reconnect if not connected
  if (!mqtt_client.connected()) {
    reconnect();
  }

  mqtt_client.loop();  // Ensure MQTT client stays connected
  resetButton.tick();
  checkGoal(sensorPinBlue, &counterBlue, "blue", tresholdBlue);
  checkGoal(sensorPinRed, &counterRed, "red", tresholdRed);
  // Serial.println(analogRead(sensorPinRed));
}

void checkGoal(int sensorPin, int *counter, String team, int treshold) {
  int value = analogRead(sensorPin);

  if (value >= treshold) {
    (*counter)++;

    if (*counter >= 12){
      Serial.println("Goal " + team);
      if (team == "red"){
        score_red++;
        mqtt_client.publish(mqtt_topic_red, String(score_red).c_str());

      } else {
        score_blue++;
        mqtt_client.publish(mqtt_topic_blue, String(score_blue).c_str());

      }
      *counter = 0;
      Serial.println(value);
      delay(DELAY);
    }
  } else {
    *counter = 0;
  }
}

int getTreshold(int sensorPin) {
  int iterations = 10;
  int total = 0;

  for (int i = 0; i < iterations; i++) {
    total += analogRead(sensorPin);
  }

  return (total/iterations) * 1.1;
}

void reconnect() {
  // Loop until the client is connected
  while (!mqtt_client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Try to connect using client ID, username, and password
    if (mqtt_client.connect("ESP32Client", mqtt_user, mqtt_pass)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void connect_wifi(){
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  // Disable SSL certificate validation (Not secure!)
  client.setInsecure();

  if (client.connect("your-server.com", 443)) {
    Serial.println("Connected without SSL validation!");
  } else {
    Serial.println("Connection failed.");
  }
}


void handleReset() {
  Serial.println("reset");
  score_blue = 0;
  score_red = 0;
  mqtt_client.publish(mqtt_topic_red, String(score_red).c_str());
  mqtt_client.publish(mqtt_topic_blue, String(score_blue).c_str());

}