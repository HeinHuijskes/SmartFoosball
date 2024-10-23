#define WAVE_TIME 5

void my_fill_solid(struct CRGB * leds, int numToFill, const struct CRGB& color) {
  for (int i = 0; i < numToFill; i++) {
    leds[i] = color;
  }
}

void my_fill_solid_2(CRGB color) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;
  }
  FastLED.show();
}

void works() {
  CHSV color = CHSV(gHue, 255, 255);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;
  }
}

void goalRedLights(void *parameter) {
  // CRGB color = (CRGB) &parameter;
  CRGB color = red;
  CRGB background = CRGB(255, 128, 100);
  waveUp(color, background);
  blinkAmount(color,  background, 5);
  waveDown(background, color);
  vTaskDelete(NULL);
}

void goalBlueLights(void *parameter) {
  // CRGB color = (CRGB *) &parameter;
  CRGB color = blue;
  CRGB background = CRGB(255, 128, 100);
  waveUp(color, background);
  blinkAmount(color,  background, 5);
  waveDown(background, color);
  vTaskDelete(NULL);
}

void waveUp(CRGB color, CRGB colorBackground) {
  my_fill_solid_2(colorBackground);
  FastLED.show();

  for (int i = 0; i < NUM_LEDS/2; i++) {
    leds[i] = color;
    leds[NUM_LEDS-1-i] = color;
    FastLED.show();            
    delay(WAVE_TIME);                 
  }
}

void waveDown(CRGB color, CRGB colorBackground) {
  my_fill_solid_2(colorBackground);
  FastLED.show();

  for (int i = NUM_LEDS/2; i >= 0; i--) {
    leds[i] = color; 
    leds[NUM_LEDS-1-i] = color;
    FastLED.show();  
    delay(WAVE_TIME);
  }
}

void blinkAmount(CRGB color, CRGB colorBackground, int amount) {
  int delayTime = 50;
  my_fill_solid_2(colorBackground);
  FastLED.show();
  delay(delayTime);

  for (int i = 0; i < amount; i++) {
    my_fill_solid_2(color);       
    FastLED.show();
    delay(delayTime);             
    my_fill_solid_2(colorBackground);             
    FastLED.show();               
    delay(delayTime);             
  }
}