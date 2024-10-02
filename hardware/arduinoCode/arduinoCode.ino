#define LED_PIN 5

int sensorPinBlue = 34; //define analog pin 2
int buttonPin = 3;
int valueBlue = 0;
int counter = 0;
int blueGoals = 0;





void setup() {
	Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
	valueBlue = analogRead(sensorPinBlue);

  if (valueBlue >= 950) {
    Serial.println("Goal red");
    blueGoals += 1;
    counter = 0;
    while(analogRead(sensorPinBlue) >= 950){

    }

  }

  if (digitalRead(buttonPin)) {
    Serial.println("reset");
  }
}