 # Verify P2N2222A Amplifier Transistor
in this practice, it implement the common-emitter digital switch test on P2N2222A Amplifier Transistor with ESP32, for the device specification and application circuit, please refer to P2N2222A datasheet.

# Components
* ESP32 WeMos LOLIN D32
* USB
* Breadboard
* wires
* 1 unit of P2N2222A Amplifier Transistor
* 1 unit of 2.2K ohm resistor
* 1 unit of 220 ohm resistor

# Software
* IDE: Arduino IDE

# Wiring

| P2N2222A | description | ESP32 |
| ---- | ----------- | --- |
| Collector | 220 ohm serial connected to power | 3.3V |
| Collector | parallel connected | GPIO34 |
| Base | 2.2K ohm serial connected | GPIO25 |
| Emitter | ground | GND |

# Code
This program tests the P2N2222A transistor's functionality as a common-emitter digital switch. It drives the base HIGH and LOW and verifies that the collector voltage switches accordingly.

Test Flow:
1. Initialize GPIO pins.
2. Test OFF State: Drive Base LOW, expect Collector to be HIGH.
3. Test ON State: Drive Base HIGH, expect Collector to be LOW.
4. Repeat the test cycle.
```C++
// Pin definitions based on pin_define-P2N2222A.json
const int BASE_PIN = 25;      // ESP32 pin connected to the transistor's base (via RB)
const int COLLECTOR_PIN = 34; // ESP32 pin to sense the transistor's collector voltage

// Test cycle delay
const unsigned long TEST_INTERVAL_MS = 5000;

void setup() {
  // Start serial communication for outputting test results
  Serial.begin(115200);
  // Wait a moment for the serial monitor to connect
  delay(1000);

  Serial.println("--- P2N2222A NPN Transistor Switching Test Initializing ---");

  // Configure pin modes
  // BASE_PIN is an output to control the transistor
  pinMode(BASE_PIN, OUTPUT);
  // COLLECTOR_PIN is an input to read the transistor's state
  pinMode(COLLECTOR_PIN, INPUT);

  // Set the initial state to OFF
  digitalWrite(BASE_PIN, LOW);
  Serial.println("Initialization complete. Starting test loop...");
}

void loop() {
  // --- Test OFF State (Cutoff) ---
  Serial.println("\n------------------------------------");
  Serial.println("Step 1: Testing OFF State (Cutoff)");
  Serial.println("Action: Driving Base pin LOW to turn transistor OFF.");

  // Drive the base low
  digitalWrite(BASE_PIN, LOW);

  // Allow a brief moment for the circuit to stabilize
  delay(100);

  // Read the state of the collector
  int collectorStateOff = digitalRead(COLLECTOR_PIN);

  Serial.print("  -> Expected Collector State: HIGH (1)\n");
  Serial.print("  -> Observed Collector State: ");
  Serial.println(collectorStateOff);

  // Verify the result
  if (collectorStateOff == HIGH) {
    Serial.println("Result: PASS - Transistor is correctly in cutoff state.");
  } else {
    Serial.println("Result: FAIL - Transistor is not in cutoff state. Collector should be HIGH.");
  }

  // Wait before the next test
  delay(TEST_INTERVAL_MS / 2);


  // --- Test ON State (Saturation) ---
  Serial.println("\nStep 2: Testing ON State (Saturation)");
  Serial.println("Action: Driving Base pin HIGH to turn transistor ON.");

  // Drive the base high
  digitalWrite(BASE_PIN, HIGH);

  // Allow a brief moment for the circuit to stabilize
  delay(100);

  // Read the state of the collector
  int collectorStateOn = digitalRead(COLLECTOR_PIN);

  Serial.print("  -> Expected Collector State: LOW (0)\n");
  Serial.print("  -> Observed Collector State: ");
  Serial.println(collectorStateOn);

  // Verify the result
  if (collectorStateOn == LOW) {
    Serial.println("Result: PASS - Transistor is correctly in saturation state.");
  } else {
    Serial.println("Result: FAIL - Transistor is not in saturation state. Collector should be LOW.");
  }

  // Wait for the specified interval before repeating the cycle
  Serial.println("------------------------------------");
  Serial.println("Test cycle complete. Restarting soon...");
  delay(TEST_INTERVAL_MS / 2);
}
```
