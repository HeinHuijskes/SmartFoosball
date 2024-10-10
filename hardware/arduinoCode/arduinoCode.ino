#include <OneButton.h>
#define BUTTON_PIN 26
#define DELAY 2000

int sensorPinBlue = 34; //define analog pin 2
int sensorPinRed = 35; //define analog pin 3
// int valueBlue = 0;
int counterBlue = 0;
int counterRed = 0;
int blueGoals = 0;
int tresholdBlue = 850;
int tresholdRed = 700;
OneButton resetButton;

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


  Serial.println("start");


}

void loop() {
  resetButton.tick();
  checkGoal(sensorPinBlue, &counterBlue, "blue", tresholdBlue);
  checkGoal(sensorPinRed, &counterRed, "red", tresholdRed);

  // Serial.println(analogRead(sensorPinRed));
}

void checkGoal(int sensorPin, int *counter, String team, int treshold) {
  int value = analogRead(sensorPin);

  if (value >= treshold) {
    (*counter)++;

    if (*counter >= 6){
      Serial.println("Goal " + team);
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


static void handleReset() {
  Serial.println("reset");
}