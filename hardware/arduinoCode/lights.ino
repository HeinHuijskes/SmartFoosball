#define WAVE_TIME 5

/*
This function gives all the LEDs in an array the same color.

Input:
  CRGB color: the color for the LEDs
  CRGB leds[]: the LED-strip to color
  int size: the size of the LED-strip

Output:
  There is no return value, but all the LEDs in an array will have the same color.
*/
void fillSolid(CRGB color, CRGB leds[], int size) {
  for (int i = 0; i < size; i++) {
    leds[i] = color;
  }
  FastLED.show();
}

/*
This function gives the bottom of one of the LED-beams, i.e. the outer edges of the
LED-strip, the same color.

Input:
  CRGB color: the color for the LEDs
  CRGB leds[]: the LED-strip to color
  int size: the size of the LED-strip
  int amount: how far the LED-strip should be filled

Output:
  There is no return value, but the outer edges of a LED-strip will have a different
  color than inside.
*/
void fillBottom(CRGB color, CRGB leds[], int size, int amount) {
  for (int i = 0; i < amount; i++) {
    leds[i] = color;
    leds[size - i - 1] = color;
  }
  FastLED.show();
}

/*
This function performs an animation when the red team made a goal on its own core.

Output:
  There is no return value, but a random animation will play for the red team.
*/
void goalRedLights(void *parameter) {
  if (random(0, 2) == 0) {
    animationRed1();
  } else {
    animationRed2();
  }

  vTaskDelete(NULL);
}

/*
One of the two animations for when team red scores.

Output:
  There is no return value, but red ligths will move upwards,
  blink 5 times and move downwards again.
*/
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

/*
One of the two animations for when team red scores.

Output:
  There is no return value, but red lights will move across the beams and then go to the red side.
*/
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

/*
This function performs an animation when the blue team made a goal on its own core.

Output:
  There is no return value, but a random animation will play for the blue team.
*/
void goalBlueLights(void *parameter) {
  if (random(0, 2) == 0) {
    animationBlue1();
  } else {
    animationBlue2();
  }
  vTaskDelete(NULL);
}

/*
One of the two animations for when team blue scores.

Output:
  There is no return value, but blue ligths will move upwards,
  blink 5 times and move downwards again.
*/
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

/*
One of the two animations for when team blue scores.

Output:
  There is no return value, but blue lights will move across the beams and then go to the blue side.
*/
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

/*
Animation where colors move upwards across the side beams and inwards across the top beam

Input:
  CRGB color1: the color for the beam of the blue side
  CRGB color2: the color for the beam of the red side
  CRGB color3: the color for the top beam
*/
void waveUp(CRGB color1, CRGB color2, CRGB color3) {
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

/*
Animation where colors move outwards across the top beam and downwards across the side beams

Input:
  CRGB color1
*/
void waveDown(CRGB color1, CRGB color2, int mode) {  // mode 0 is both sides, mode 1 is red side, mode -1 is blue side
  for (int i = NUM_LEDS_BLUE / 2; i >= 0; i--) {
    if (mode <= 0) {  // blue side
      ledsBlue[i] = pink;
      ledsBlue[NUM_LEDS_BLUE - 1 - i] = pink;

      if (i + score_blue <= NUM_LEDS_BLUE / 2) {
        ledsBlue[i + score_blue] = color1;
        ledsBlue[NUM_LEDS_BLUE - 1 - i - score_blue] = color1;
      }
    }

    if (mode >= 0) {  // red side
      ledsRed[i] = green;
      ledsRed[NUM_LEDS_RED - 1 - i] = green;

      if (i + score_red <= NUM_LEDS_RED / 2) {
        ledsRed[i + score_red] = color2;
        ledsRed[NUM_LEDS_RED - 1 - i - score_red] = color2;
      }
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
  for (int i = NUM_LEDS_TOP - 1; i >= NUM_LEDS_TOP - 1 - offset; i--) {
    ledsTop[i] = color2;
    FastLED.show();
    delay(WAVE_TIME);
  }

  for (int i = NUM_LEDS_TOP - 1; i >= offset; i--) {
    ledsTop[i] = color1;
    ledsTop[i - offset] = color2;
    FastLED.show();
    delay(WAVE_TIME);
  }
}

void waveRight(CRGB color1, CRGB color2, int offset) {
  for (int i = 0; i < offset; i++) {
    ledsTop[i] = color2;
    FastLED.show();
    delay(WAVE_TIME);
  }

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