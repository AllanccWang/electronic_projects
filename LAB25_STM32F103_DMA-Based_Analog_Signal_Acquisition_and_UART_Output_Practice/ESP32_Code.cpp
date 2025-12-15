/*
 * ESP32 DAC Signal Generator for STM32 ADC Verification
 *
 * Wiring:
 * ESP32 GPIO 25 (DAC1) -> STM32 PA0
 * ESP32 GPIO 26 (DAC2) -> STM32 PA1
 * ESP32 GND            -> STM32 GND
 */

// DAC pin definitions
const int DAC_PIN_1 = 25; 
const int DAC_PIN_2 = 26;

void setup() {
  Serial.begin(115200);
  Serial.println("=== ESP32 DAC Signal Generator Started ===");
  Serial.println("Generating signals on GPIO 25 & 26...");
}

void loop() {
  // Generate a triangle wave sweeping from 0V to 3.3V
  // DAC resolution is 8-bit (0–255)
  
  // 1. Rising ramp (Ramp Up)
  for (int value = 0; value <= 255; value += 5) {
    dacWrite(DAC_PIN_1, value);           // PA0 receives the varying voltage
    dacWrite(DAC_PIN_2, 255 - value);     // PA1 receives the inverted voltage
    
    // Calculate expected voltage and print it (for comparison with STM32 output)
    float voltage = (value / 255.0) * 3.3;
    Serial.printf("ESP32 Out: %d (%.2f V)\n", value, voltage);
    
    delay(50); // Small delay to give STM32 time to read
  }

  // 2. Falling ramp (Ramp Down)
  for (int value = 255; value >= 0; value -= 5) {
    dacWrite(DAC_PIN_1, value);
    dacWrite(DAC_PIN_2, 255 - value);
    
    float voltage = (value / 255.0) * 3.3;
    Serial.printf("ESP32 Out: %d (%.2f V)\n", value, voltage);
    
    delay(50);
  }
}