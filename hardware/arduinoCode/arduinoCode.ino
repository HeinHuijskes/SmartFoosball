int sensorPinBlue = 34; //define analog pin 2
// int sensorPinRed = 35; //define analog pin 3
int valueBlue = 0;
// int valueRed = 0;
int counter = 0;
int blueGoals = 0;


void setup() {
	Serial.begin(9600);
}

void loop() {
	valueBlue = analogRead(sensorPinBlue);

  if (valueBlue >= 950) {
    Serial.println("Goal blue");
    blueGoals += 1;
    counter = 0;
    while(analogRead(sensorPinBlue) >= 950){

    }
  }
}