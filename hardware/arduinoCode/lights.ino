#define WAVE_TIME 5

void my_fill_solid(struct CRGB *ledsBlue, int numToFill, const struct CRGB &color) {
  for (int i = 0; i < numToFill; i++) {
    ledsBlue[i] = color;
  }
}

void fillSolid(CRGB color, CRGB leds[], int size) {
  for (int i = 0; i < size; i++) {
    leds[i] = color;
  }
  FastLED.show();
}

void fillBottom(CRGB color, CRGB leds[], int size, int amount) {
  for (int i = 0; i < amount; i++) {
    leds[i] = color;
    leds[size - i - 1] = color;
  }
  FastLED.show();
}

void works() {
  CHSV color = CHSV(gHue, 255, 255);
  for (int i = 0; i < NUM_LEDS_BLUE; i++) {
    ledsBlue[i] = color;
  }
}

void goalRedLights(void *parameter) {
  if (random(0, 2) == 0) {
    animationRed1();
  } else {
    animationRed2();
  }
  
  vTaskDelete(NULL);
}

void animationRed1() {
  fillSolid(black, ledsBlue, NUM_LEDS_BLUE);
  fillSolid(black, ledsRed, NUM_LEDS_RED);
  fillSolid(black, ledsTop, NUM_LEDS_TOP);
  waveUp(red, red, red);
  blinkAmount(red, black, 5);
  waveOutwards(white, pink, green, score_blue, score_red);
  fillSolid(white, ledsTop, NUM_LEDS_TOP);
  waveDown(blue, red, 0);
}

void animationRed2() {
  fillSolid(black, ledsBlue, NUM_LEDS_BLUE);
  fillSolid(black, ledsRed, NUM_LEDS_RED);
  fillSolid(black, ledsTop, NUM_LEDS_TOP);
  waveOpposites(red);
  waveOpposites(black);
  waveRight(white, green, score_red);
  fillSolid(white, ledsTop, NUM_LEDS_TOP);
  waveDown(black, red, 1);
  fillSolid(blue, ledsBlue, NUM_LEDS_BLUE);
  fillBottom(pink, ledsBlue, NUM_LEDS_BLUE, score_blue);
}

void goalBlueLights(void *parameter) {
  if (random(0, 2) == 0) {
    animationBlue1();
  } else {
    animationBlue2();
  }
  vTaskDelete(NULL);
}

void animationBlue1() {
  fillSolid(black, ledsBlue, NUM_LEDS_BLUE);
  fillSolid(black, ledsRed, NUM_LEDS_RED);
  fillSolid(black, ledsTop, NUM_LEDS_TOP);
  waveUp(blue, blue, blue);
  blinkAmount(blue, black, 5);
  waveOutwards(white, pink, green, score_blue, score_red);
  fillSolid(white, ledsTop, NUM_LEDS_TOP);
  waveDown(blue, red, 0);
}

void animationBlue2() {
  fillSolid(black, ledsBlue, NUM_LEDS_BLUE);
  fillSolid(black, ledsRed, NUM_LEDS_RED);
  fillSolid(black, ledsTop, NUM_LEDS_TOP);
  waveOpposites(blue);
  waveOpposites(black);
  waveLeft(white, pink, score_blue);
  fillSolid(white, ledsTop, NUM_LEDS_TOP);
  waveDown(blue, black, -1);
  fillSolid(red, ledsRed, NUM_LEDS_RED);
  fillBottom(green, ledsRed, NUM_LEDS_RED, score_red);
}

void waveUp(CRGB color1, CRGB color2, CRGB color3) {
  // fillSolid(colorBackground, ledsBlue, NUM_LEDS_BLUE);
  // fillSolid(colorBackground, ledsRed, NUM_LEDS_RED);
  // fillSolid(colorBackground, ledsTop, NUM_LEDS_TOP);

  for (int i = 0; i < NUM_LEDS_BLUE / 2; i++) {
    ledsBlue[i] = color1;
    ledsBlue[NUM_LEDS_BLUE - 1 - i] = color1;
    ledsRed[i] = color2;
    ledsRed[NUM_LEDS_BLUE - 1 - i] = color2;
    FastLED.show();
    delay(WAVE_TIME);
  }

  for (int i = 0; i < NUM_LEDS_TOP / 2; i++) {
    ledsTop[i] = color3;
    ledsTop[NUM_LEDS_TOP - 1 - i] = color3;
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void waveDown(CRGB color1, CRGB color2, int mode) {  // mode 0 is both sides, mode 1 is red side, mode -1 is blue side
  // fillSolid(colorBackground, ledsBlue, NUM_LEDS_BLUE);
  // fillSolid(colorBackground, ledsRed, NUM_LEDS_RED);
  // fillSolid(colorBackground, ledsTop, NUM_LEDS_TOP);

  // for (int i = NUM_LEDS_TOP/2; i >= 0; i--) {
  //   ledsTop[i] = color3;
  //   ledsTop[NUM_LEDS_TOP-1-i] = color3;
  //   FastLED.show();
  //   delay(WAVE_TIME);
  // }

  for (int i = NUM_LEDS_BLUE / 2; i >= 0; i--) {
    if (mode <= 0) {
      ledsBlue[i] = pink;
      ledsBlue[i + score_blue] = color1;
      ledsBlue[NUM_LEDS_BLUE - 1 - i] = pink;
      ledsBlue[NUM_LEDS_BLUE - 1 - i - score_blue] = color1;
    }

    if (mode >= 0) {
      ledsRed[i] = green;
      ledsRed[i + score_red] = color2;
      ledsRed[NUM_LEDS_RED - 1 - i] = green;
      ledsRed[NUM_LEDS_RED - 1 - i - score_red] = color2;
    }
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void waveOutwards(CRGB color1, CRGB color2, CRGB color3, int amount1, int amount2) {
  for (int i = NUM_LEDS_TOP / 2; i >= 0; i--) {
    ledsTop[i] = color2;
    ledsTop[i + amount1] = color1;
    ledsTop[NUM_LEDS_TOP - 1 - i] = color3;
    ledsTop[NUM_LEDS_TOP - 1 - i - amount2] = color1;
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void waveOpposites(CRGB color) {
  for (int i = NUM_LEDS_BLUE - 1; i >= 0; i--) {
    Serial.println(i);
    ledsBlue[i] = color;
    ledsRed[NUM_LEDS_BLUE - i] = color;
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void waveLeft(CRGB color1, CRGB color2, int offset) {
  for (int i = NUM_LEDS_TOP - 1; i >= offset; i--) {
    ledsTop[i] = color1;
    ledsTop[i - offset] = color2;
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void waveRight(CRGB color1, CRGB color2, int offset) {
  for (int i = offset; i < NUM_LEDS_TOP; i++) {
    ledsTop[i - offset] = color1;
    ledsTop[i] = color2;
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void blinkAmount(CRGB color, CRGB colorBackground, int amount) {
  int delayTime = 50;
  fillSolid(colorBackground, ledsBlue, NUM_LEDS_BLUE);
  fillSolid(colorBackground, ledsRed, NUM_LEDS_RED);
  fillSolid(colorBackground, ledsTop, NUM_LEDS_TOP);
  delay(delayTime);

  for (int i = 0; i < amount; i++) {
    fillSolid(color, ledsBlue, NUM_LEDS_BLUE);
    fillSolid(color, ledsRed, NUM_LEDS_RED);
    fillSolid(color, ledsTop, NUM_LEDS_TOP);
    delay(delayTime);

    fillSolid(colorBackground, ledsBlue, NUM_LEDS_BLUE);
    fillSolid(colorBackground, ledsRed, NUM_LEDS_RED);
    fillSolid(colorBackground, ledsTop, NUM_LEDS_TOP);
    delay(delayTime);
  }
}