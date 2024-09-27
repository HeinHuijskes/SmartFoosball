#define LED_PIN 5

int sensorPinBlue = 34; //define analog pin 2
// int sensorPinRed = 35; //define analog pin 3
int valueBlue = 0; 
// int valueRed = 0;





void setup() {
	Serial.begin(9600); 
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  // analogWrite(LED_PIN, 20);

} 

void loop() {
	valueBlue = analogRead(sensorPinBlue); 
	Serial.println(valueBlue, DEC); // light intensity

  // valueRed = analogRead(sensorPinRed); 
	// Serial.println(valueRed, DEC); // light intensity
  // value = 0;
	// delay(100); 
  // goal if value is higher than... for a length of...
  // determine the team
  // if goal, send call to endpoint laptop -> we need wifi on the esp
  // later:update LEDs
}