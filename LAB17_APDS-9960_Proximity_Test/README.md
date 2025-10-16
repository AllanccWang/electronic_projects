# APDS-9960 – Proximity Function Test (Validation with Force-to-Fail)

The **APDS-9960** is a digital sensor that integrates proximity, gesture, ambient light, and RGB color detection.  
This test validates the **proximity detection** functionality by interfacing the sensor with an ESP32 development board.  
The validation includes **force-to-fail wiring scenarios** to ensure the test logic can detect incorrect connections.

---

## Components

- ESP32 Development Board (e.g., NodeMCU-32S, LOLIN D32)
- USB cable
- Breadboard
- Jumper wires
- 1 × APDS-9960 Sensor Module

Optional for Force-to-Fail Testing
- 2 x 1N4001 diodes

---

## Software

- **IDE**: Arduino IDE (or PlatformIO)
- **Required Library**: [SparkFun APDS9960 RGB and Gesture Sensor](https://github.com/sparkfun/SparkFun_APDS-9960_Sensor_Arduino_Library)  
  Install via Arduino IDE Library Manager.

---

## Wiring

### ✅ Correct Wiring (Functional Test)

| APDS-9960 Pin | Description | ESP32 Pin |
|---------------|-------------|-----------|
| VCC           | Power (3.3V only) | 3.3V |
| GND           | Ground | GND |
| SDA           | I²C Data | GPIO21 |
| SCL           | I²C Clock | GPIO22 |
| INT           | Interrupt (not used in this test) | — |

⚠️ **Note**: The APDS-9960 operates at **3.3V logic**. Do not connect to 5V.

---

## Code
- **Serial Baud Rate**: 115200  
- **Proximity Threshold**: 50 (0–255 range, adjustable)  
- **Timeout**: 10 seconds per test cycle  

1. Upload the `APDS-9960_Proximity_Test.cpp` sketch to the ESP32.
2. Open the Serial Monitor at **115200 baud**.
3. The program initializes the APDS-9960 sensor and enables proximity detection.
4. Follow the prompts:
   - Place an object near the sensor → proximity value rises above threshold.
   - Remove the object → proximity value falls below threshold.
5. For **force-to-fail cases**, deliberately miswire as described below and confirm that the test detects the failure. Results are [_here_](LAB17_APDS-9960_Proximity_Test/APDS-9960_Proximity_Test_Results.txt)
   - no object near to sensor
   - Violate the minimum VIH of 2.31V on the SDA line
   - Undervoltage Lockout (UVLO)-Drop Vcc below 2.4V(with 2 series diodes) to force the internal UVLO circuit to trigger.
```C++
#include <Wire.h>
#include <SparkFun_APDS9960.h>

// --- Test Parameters ---
// Pin Definitions (for ESP32, change if using another board)
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;

// Serial Configuration
const long SERIAL_BAUD_RATE = 115200;

// Proximity Test Configuration
// Threshold for detecting an object. Range is 0-255.
// Adjust this value based on environmental conditions and desired sensitivity.
const uint8_t PROXIMITY_THRESHOLD = 50;
// Timeout in milliseconds to wait for user action (placing/removing object).
const unsigned long TEST_TIMEOUT_MS = 10000;

// Global sensor object
SparkFun_APDS9960 apds = SparkFun_APDS9960();

// --- Test State Machine ---
enum TestState {
  WAIT_FOR_OBJECT,
  WAIT_FOR_REMOVAL,
  TEST_CYCLE_COMPLETE
};
TestState currentState = WAIT_FOR_OBJECT;


/**
 * @brief Initializes serial communication, I2C, and the APDS-9960 sensor.
 */
void setup() {
  // 1. Initialize Serial communication
  Serial.begin(SERIAL_BAUD_RATE);
  while (!Serial); // Wait for Serial port to connect
  Serial.println();
  Serial.println("--- APDS-9960 Proximity Function Test ---");
  Serial.println("Initializing...");

  // 2. Initialize I2C communication
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  // 3. Initialize the APDS-9960 sensor
  if (apds.init()) {
    Serial.println("-> APDS-9960 initialization complete.");
  } else {
    Serial.println("-> ERROR: APDS-9960 initialization failed. Check connections and I2C address.");
    while (1); // Halt execution
  }

  // 4. Enable the Proximity sensor
  // Second parameter 'true' enables proximity interrupts, but we will poll data directly.
  if (apds.enableProximitySensor(false)) {
    Serial.println("-> Proximity sensor is now active.");
  } else {
    Serial.println("-> ERROR: Could not enable proximity sensor.");
    while (1); // Halt execution
  }

  Serial.println("-------------------------------------------");
  Serial.println("Setup complete. Starting test loop.");
}

/**
 * @brief Runs the main test sequence for proximity detection.
 */
void loop() {
  uint8_t proximity_value = 0;
  static unsigned long startTime;

  switch (currentState) {
    case WAIT_FOR_OBJECT:
      Serial.println("\n[TEST STEP 1/2] Please place an object within 5cm of the sensor...");
      startTime = millis();
      currentState = (TestState)-1; // Intermediate state to prevent re-entry message spam

      // This loop will run until an object is detected or a timeout occurs
      while (millis() - startTime < TEST_TIMEOUT_MS) {
        // Read the proximity value
        if (apds.readProximity(proximity_value)) {
          Serial.print("."); // Print progress indicator
          // Check if the value is above our detection threshold
          if (proximity_value > PROXIMITY_THRESHOLD) {
            Serial.println("\n-> PASS: Object detected!");
            Serial.print("   Proximity Value: ");
            Serial.println(proximity_value);
            currentState = WAIT_FOR_REMOVAL;
            return; // Exit the switch and restart loop for the next state
          }
        } else {
          Serial.println("\n-> ERROR: Could not read proximity value.");
        }
        delay(250); // Poll every 250ms
      }

      // If we reach here, the test timed out
      Serial.println("\n-> FAIL: Test timed out waiting for object.");
      currentState = TEST_CYCLE_COMPLETE;
      break;

    case WAIT_FOR_REMOVAL:
      Serial.println("\n[TEST STEP 2/2] Please remove the object from the sensor...");
      startTime = millis();
      currentState = (TestState)-1; // Intermediate state

      while (millis() - startTime < TEST_TIMEOUT_MS) {
        if (apds.readProximity(proximity_value)) {
          Serial.print(".");
          if (proximity_value < PROXIMITY_THRESHOLD) {
            Serial.println("\n-> PASS: Object removed!");
            Serial.print("   Proximity Value: ");
            Serial.println(proximity_value);
            currentState = TEST_CYCLE_COMPLETE;
            return;
          }
        } else {
          Serial.println("\n-> ERROR: Could not read proximity value.");
        }
        delay(250);
      }

      Serial.println("\n-> FAIL: Test timed out waiting for object removal.");
      currentState = TEST_CYCLE_COMPLETE;
      break;

    case TEST_CYCLE_COMPLETE:
      Serial.println("\n--- Test Cycle Finished ---");
      Serial.println("Restarting in 10 seconds...");
      delay(10000);
      currentState = WAIT_FOR_OBJECT; // Reset for the next run
      break;

    default:
      // This is an intermediate state, do nothing
      break;
  }
}
```