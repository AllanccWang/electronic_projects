## 🌐 Project : STM32-ESP32 Dual MCU Communication Setup

This document summarizes the established and validated communication configuration between the STM32F103C8T6 (processing core) and the ESP32 (connectivity core), utilizing the CP2102 for programming and debugging.

---

### I. 🎯 Purpose and Roles

| Device | Role in the System | Primary Function |
| :---: | :---: | :---: |
| **STM32F103C8T6** | **Processing/Sensor Core** | High-speed data acquisition and UART transmission to the ESP32. |
| **ESP32** | **Connectivity Core** | Receives processed data from the STM32, manages Wi-Fi/Cloud connectivity, and acts as the system interface. |
| **CP2102 (USB-to-TTL)** | **Programmer/Debugger** | Used to flash (upload) the application code to the STM32 and, during execution, monitor debug output. |

---

### II. 🔗 Pin Connection Diagrams

To avoid signal conflicts, the STM32's two UART ports are strategically used for different purposes.

#### 1. Programming Connection (CP2102 ↔ STM32)

- **Usage:** Only required during the application upload process.  
- **Requirement:** STM32 must be in **Bootloader Mode** (i.e., **BOOT0=1**).

| STM32 (F103C8T6) | CP2102 (USB-to-TTL) | Logic Function (STM32) |
| :---: | :---: | :---: |
| **PA10** | **TX0** | USART1_RX (Bootloader Receive) |
| **PA9** | **RX0** | USART1_TX (Bootloader Transmit) |
| **3.3V** | **3V3** | Power Supply |
| **GND** | **GND** | Common Ground |

#### 2. Application Communication Connection (ESP32 ↔ STM32)

- **Usage:** Required during normal program execution.  
- **Requirement:** STM32 must be in **Program Execution Mode** (i.e., **BOOT0=0**).

| STM32 (F103C8T6) | ESP32 (Dev Board) | Logic Function (STM32) |
| :---: | :---: | :---: |
| **PA3** | **GPIO17 (TX)** | USART2_RX (Receive from ESP32) |
| **PA2** | **GPIO16 (RX)** | USART2_TX (Transmit to ESP32) |
| **GND** | **GND** | Common Ground |

---

### III. 💻 Code Logic

The following code establishes a robust, two-way communication channel using the configured pins.

#### 1. STM32 Code (Receiver/Processor)

- **Purpose:** Listens on `Serial2` for ESP32 data, processes it, and sends an acknowledgment (ACK). It uses the Blue Pill's on-board LED (`PC13`) to signal successful data reception.

```cpp
// STM32 Code (Roger Clark/Maple Core)

const int LED_PIN = PC13; 

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // LED OFF (High)
  
  // Initialize communication with ESP32 on USART2 (PA2/PA3)
  Serial2.begin(115200); 
}

void loop() {
  // Check for incoming data from ESP32 (on PA3/RX2)
  if (Serial2.available()) {
    String incomingData = Serial2.readStringUntil('\n');
    
    // 1. Indication: Blink LED
    digitalWrite(LED_PIN, LOW); // LED ON
    
    // 2. Data Processing (Placeholder for sensor data logic)
    // ... Process incomingData here ...
    
    // 3. Send Acknowledgment (ACK) back to ESP32 (on PA2/TX2)
    Serial2.print("STM32 ACK: Received ");
    Serial2.println(incomingData.length()); 
    
    delay(50); 
    digitalWrite(LED_PIN, HIGH); // LED OFF
  }
}
```

#### 2. ESP32 Code (Sender/Monitor)

- **Purpose:** Uses `Serial2` to send test data to the STM32 and monitors the same port for the STM32's ACK message. Output is monitored via the USB serial monitor (`Serial.begin`).

```cpp
// ESP32 Code (Arduino Core)

#include <HardwareSerial.h>
HardwareSerial Serial_to_STM32(2); 

const int TX_PIN_TO_STM32 = 17; // TX -> STM32 RX (PA3)
const int RX_PIN_FROM_STM32 = 16; // RX <- STM32 TX (PA2)

void setup() {
  Serial.begin(115200); // USB Debug Output
  
  // Initialize communication with STM32, specifying pins
  Serial_to_STM32.begin(115200, SERIAL_8N1, RX_PIN_FROM_STM32, TX_PIN_TO_STM32);
  Serial.println("\n--- ESP32 Initialized ---");
}

int counter = 0;

void loop() {
  // 1. Send data to STM32
  String message = "ESP32 -> STM32 Test Count: " + String(counter++);
  Serial_to_STM32.println(message); 
  Serial.println("Sent: " + message); 

  // 2. Receive ACK from STM32
  if (Serial_to_STM32.available()) {
    String ackMessage = Serial_to_STM32.readStringUntil('\n');
    Serial.print("Received from STM32: ");
    Serial.println(ackMessage);
  }
  
  delay(1000); 
}
```

---

### IV. ❓ Q&A Debug Section

| Issue/Symptom | Primary Cause | Solution |
| :---: | :---: | :---: |
| **`Failed to init device.`** | **Incorrect Boot Mode:** The STM32 is not in the Bootloader mode for programming. | Set **BOOT0=1** and **BOOT1=0**, then **press the RESET button** *before* running the `stm32flash` command. |
| **STM32 LED not blinking.** | **RX Connection Error:** STM32 is not receiving data from ESP32. | Verify the **CROSS-connection**: ESP32 TX (GPIO17) ↔ STM32 RX (PA3). |
| **ESP32 doesn't receive ACK.** | **TX Connection Error:** STM32 is not sending data or the wire is bad. | Verify the **CROSS-connection**: STM32 TX (PA2) ↔ ESP32 RX (GPIO16). |
| **ACK number (e.g., 30) is fixed.** | **Expected Behavior:** The ACK number represents the length of the string received. | This is normal as long as the counter value remains two digits (10-99). The length will change again when the counter hits 100. |