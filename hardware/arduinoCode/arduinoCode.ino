#define LED_PIN 5

int sensorPinBlue = 34; //define analog pin 2
// int sensorPinRed = 35; //define analog pin 3
int valueBlue = 0; 
// int valueRed = 0;
int counter = 0;
int blueGoals = 0;





void setup() {
	Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  // analogWrite(LED_PIN, 20);

}

void loop() {
	valueBlue = analogRead(sensorPinBlue);

  if (valueBlue >= 950) {
	  // Serial.println(valueBlue, DEC); // light intensity
    // counter +=1;

    Serial.println("Goal red");
//     Serial.println(blueGoals);
    blueGoals += 1;
    counter = 0;
    while(analogRead(sensorPinBlue) >= 950){

    }

  }


  // valueRed = analogRead(sensorPinRed); 
	// Serial.println(valueRed, DEC); // light intensity
  // value = 0;
	// delay(100); 
  // goal if value is higher than... for a length of...
  // determine the team
  // if goal, send call to endpoint laptop -> we need wifi on the esp
  // later:update LEDs
}