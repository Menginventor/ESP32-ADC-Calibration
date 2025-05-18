// ESP32 DAC
#include "adc_correction_lookup.h"




#define DAC1_PIN 25
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    char ser = Serial.read();
    for (int val = 0; val < 256; val++) {
      dacWrite(DAC1_PIN, val);

      delay(1);
      for (int i = 0; i < 100; i++) {
        int adc_val = analogRead(33);
        Serial.print(val);
        Serial.print('\t');
         Serial.print(adc_val);
        Serial.print('\t');
        uint16_t corrected = adc_correction_lut[analogRead(33)];
        Serial.println(corrected);
      }
    }
  }
}
