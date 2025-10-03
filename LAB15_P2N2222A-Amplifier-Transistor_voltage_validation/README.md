# P2N2222A-Amplifier-Transistor voltage validation
Voltage Level Validation for P2N2222A NPN Transistor Using ESP32 ADC.
To verify the switching behavior of the P2N2222A transistor by measuring its collector voltage in both ON and OFF states using ESP32’s ADC. This test ensures:
* The transistor enters saturation when the base is driven HIGH, resulting in a collector voltage near 0–0.4V.
* The transistor enters cutoff when the base is driven LOW, resulting in a collector voltage near VCC (≈3.3V).
* The test logic can detect failure conditions, such as disconnected base, grounded collector, or floating inputs.
This complements the LAB14 digital switch test by adding analog precision and robustness to your diagnostic framework.

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
<img align="justify" src="https://github.com/AllanccWang/electronic_projects/blob/be0a2c0213b3476932db2d1263b9f268e6106e26/LAB14_Verify_P2N2222A_Amplifier-Transistor_Switching/P2N2222A_Transistor_Wiring.jpg" alt="P2N2222A_ESP32_Wiring_02" style="width:80%">

# Code
Test Flow:
1. Initialize GPIO pins and ADC configuration.
2. Test OFF State: Drive Base LOW, measure Collector voltage via ADC, expect ≈ VCC (3.0–3.3V).
3. Test ON State: Drive Base HIGH, measure Collector voltage via ADC, expect ≈ 0.0–0.4V.
4. Validate voltage ranges and log PASS/FAIL results.
5. Repeat the test cycle at defined intervals.

Please refer the [_P2N2222A_voltage_validation_Results_Pass_and_fail_](https://github.com/AllanccWang/electronic_projects/blob/4fc298cad8bde9c6be9c640f2d5b02a52998e878/LAB15_P2N2222A-Amplifier-Transistor_voltage_validation/P2N2222A_voltage_validation_Results_Pass_and_fail.txt) for results.

```C++
const int BASE_PIN = 25;        // Output to transistor base
const int COLLECTOR_ADC = 34;   // ADC input from transistor collector

const unsigned long TEST_INTERVAL_MS = 5000;
const float ADC_REF_VOLTAGE = 3.3; // ESP32 ADC reference voltage
const int ADC_RESOLUTION = 4095;   // 12-bit ADC

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("--- P2N2222A Voltage Level Validation Test ---");

  pinMode(BASE_PIN, OUTPUT);
  pinMode(COLLECTOR_ADC, INPUT);

  digitalWrite(BASE_PIN, LOW);
  Serial.println("Initialization complete. Starting test loop...");
}

void loop() {
  // --- OFF State Test ---
  Serial.println("\n[OFF State Test]");
  digitalWrite(BASE_PIN, LOW);
  delay(100);

  int adcValueOff = analogRead(COLLECTOR_ADC);
  float voltageOff = (adcValueOff * ADC_REF_VOLTAGE) / ADC_RESOLUTION;

  Serial.print("Collector Voltage (OFF): ");
  Serial.print(voltageOff, 3);
  Serial.println(" V");

  if (voltageOff >= 3.0 && voltageOff <= 3.3) {
    Serial.println("Result: PASS - Collector is HIGH as expected.");
  } else {
    Serial.println("Result: FAIL - Collector voltage not within expected HIGH range.");
  }

  delay(TEST_INTERVAL_MS / 2);

  // --- ON State Test ---
  Serial.println("\n[ON State Test]");
  digitalWrite(BASE_PIN, HIGH);
  delay(100);

  int adcValueOn = analogRead(COLLECTOR_ADC);
  float voltageOn = (adcValueOn * ADC_REF_VOLTAGE) / ADC_RESOLUTION;

  Serial.print("Collector Voltage (ON): ");
  Serial.print(voltageOn, 3);
  Serial.println(" V");

  if (voltageOn >= 0.0 && voltageOn <= 0.4) {
    Serial.println("Result: PASS - Collector is LOW as expected.");
  } else {
    Serial.println("Result: FAIL - Collector voltage not within expected LOW range.");
  }

  delay(TEST_INTERVAL_MS / 2);
}
```
