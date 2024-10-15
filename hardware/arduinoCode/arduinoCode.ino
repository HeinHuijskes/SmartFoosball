#include <OneButton.h>
#define LED_PIN 5
#define BUTTON_PIN 26
#define DELAY 2000

int sensorPinBlue = 34; //define analog pin 2
int valueBlue = 0;
int counterBlue = 0;
int blueGoals = 0;
int treshold = 850;
OneButton resetButton;

void setup() {
	Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  resetButton = OneButton(BUTTON_PIN, true, true);
  resetButton.attachDuringLongPress(handleReset);
  Serial.println("start");
}

void loop() {
  resetButton.tick();
	valueBlue = analogRead(sensorPinBlue);
  // Serial.println(valueBlue);

  if (valueBlue >= treshold) {
    counterBlue++;

    if (counterBlue >= 6){
      Serial.println("Goal blue");
      blueGoals++;
      counterBlue = 0;
      Serial.println(valueBlue);

      delay(DELAY);

      while(valueBlue >= treshold){
        // Serial.println(valueBlue);
        delay(100);
        valueBlue = analogRead(sensorPinBlue);

      }
    }
  } else {
    counterBlue = 0;
  }
}

static void handleReset() {
  Serial.println("reset");
}