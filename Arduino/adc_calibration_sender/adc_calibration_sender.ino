// === ADC Calibration Logger for ESP32 ===
// Sends DAC value, raw ADC, and corrected ADC via Serial
// Correction table must be included via adc_correction_lookup.h

#include "adc_correction_lookup.h"

#define DAC1_PIN 25       // DAC output pin
#define ADC_PIN 33        // ADC input pin (connected to DAC output)
#define SAMPLES_PER_STEP 100
#define BAUD_RATE 115200

void setup() {
  Serial.begin(BAUD_RATE);
  while (!Serial);  // Wait for serial to be ready
}

void loop() {
  if (Serial.available() > 0) {
    char trigger = Serial.read();
    if (trigger == 'S') {  // Wait for start signal
      for (int dac_val = 0; dac_val < 256; dac_val++) {
        dacWrite(DAC1_PIN, dac_val);
        delay(1);  // allow voltage to settle

        for (int i = 0; i < SAMPLES_PER_STEP; i++) {
          int raw_adc = analogRead(ADC_PIN);
          uint16_t corrected = adc_correction_lut[raw_adc];

          Serial.print(dac_val);
          Serial.print('\t');
          Serial.print(raw_adc);
          Serial.print('\t');
          Serial.println(corrected);
        }
      }
    }
  }
}
