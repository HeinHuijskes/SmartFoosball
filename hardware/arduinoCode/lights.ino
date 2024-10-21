void my_fill_solid(struct CRGB * leds, int numToFill, const struct CRGB& color) {
  for (int i = 0; i < numToFill; i++) {
    leds[i] = color;
  }
}

void my_fill_solid_2(CHSV color) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;
  }
}

void works() {
  CHSV color = CHSV(gHue, 255, 255);
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;
  }
}

void lightLoop(void * parameter) {
  while(true) {
    // CHSV color = CHSV(gHue, 255, 255); //rainbow :D
    CHSV red = CHSV(0, 255, 255);   // Red color in HSV
    CHSV blue = CHSV(160, 255, 255);  // Fully saturated, bright blue


    // resets
    //  fill_solid(leds, NUM_LEDS, color);
    // also resets
    //  my_fill_solid(leds, NUM_LEDS, color);
    // also resets
    //  my_fill_solid_2(color);
    // works();
    waveUp(red, blue);
    blinkAmount(red, blue, 3);
    waveDown(red, blue);
    waveUp(blue, red);
    blinkAmount(blue, red, 3);
    waveDown(blue, red);
    FastLED.show();
    // delay(8); // also resets without this delay
    gHue++;
  }
}


void waveUp(CHSV color, CHSV colorBackground) {
  my_fill_solid_2(colorBackground);
  FastLED.show();

  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;                // Set LED at position i to red
    FastLED.show();               // Update the LED strip to show the changes
    delay(30);                    // Wait for 30 milliseconds
  }
}

void blinkAmount(CHSV color, CHSV colorBackground, int amount) {
  int delayTime = 100;
  my_fill_solid_2(colorBackground);
  FastLED.show();
  delay(delayTime);

  for (int i = 0; i < amount; i++) {
    my_fill_solid_2(color);                // Set LED at position i to red
    FastLED.show();               // Update the LED strip to show the changes
    delay(delayTime);                    // Wait for 30 milliseconds
    my_fill_solid_2(colorBackground);                // Set LED at position i to red
    FastLED.show();               // Update the LED strip to show the changes
    delay(delayTime);                    // Wait for 30 milliseconds
  }
}

void waveDown(CHSV color, CHSV colorBackground) {
  my_fill_solid_2(colorBackground);
  FastLED.show();

  for (int i = NUM_LEDS - 1; i >= 0; i--) {
    leds[i] = color;                // Set LED at position i to red
    FastLED.show();               // Update the LED strip to show the changes
    delay(30);                    // Wait for 30 milliseconds
  }
}

void wave(CHSV color) {
  CHSV white = CHSV(0, 0, 255);   // White in HSV (no hue, no saturation, full brightness)
  // CHSV rainbow = CHSV(gHue, 255, 255); //rainbow :D


  // First loop: turn each LED red, one by one
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;                // Set LED at position i to red
    FastLED.show();               // Update the LED strip to show the changes
    delay(30);                    // Wait for 30 milliseconds
  }

  // Optional: hold the red for a while before transitioning to white
  delay(200);                     // Keep the red color for 500 milliseconds

  // Second loop: turn each LED white, one by one
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = white;              // Set LED at position i to white
    FastLED.show();               // Update the LED strip to show the changes
    delay(30);                    // Wait for 30 milliseconds
  }

  delay(200);

  for (int i = NUM_LEDS; i > -1; i--) {
    leds[i] = color;                // Set LED at position i to red
    FastLED.show();               // Update the LED strip to show the changes
    delay(30);                    // Wait for 30 milliseconds
  }

  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = white;              // Set LED at position i to white
  }
  FastLED.show();               // Update the LED strip to show the changes


}