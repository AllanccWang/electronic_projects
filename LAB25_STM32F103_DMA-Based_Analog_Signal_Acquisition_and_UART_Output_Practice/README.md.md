## 📋 STM32F103 DMA-Based Analog Signal Acquisition and UART Output Practice

### 1. 🎯 Project Purpose

- **Core Objective:**  
  Validate the cooperative functionality of the **Analog-to-Digital Converter (ADC)** and **Direct Memory Access (DMA)** on the STM32F103 microcontroller.

- **Technical Verification:**
  - **DMA Circular Mode:**  
    Continuously and automatically write ADC data from multiple channels (PA0, PA1, PA2) into a memory buffer without interruption.
  - **UART Communication:**  
    Establish stable serial communication at **115200 baud**, sending collected data back to the PC for real‑time monitoring.
  - **Floating‑Point Handling:**  
    Use a stable **millivolt integer calculation** method to avoid issues caused by limited `sprintf` floating‑point support in embedded environments.

- **Application Value:**  
  Provides a reliable hardware/software foundation for applications requiring high‑speed, multi‑channel, background analog signal acquisition (e.g., sensor data logging, power monitoring).

---

### 2. 🔗 Pin Connections

This project consists of two parts:  
**STM32F103 (data acquisition)** and **USB‑TTL/ESP32 (communication & signal source)**.

| Device (STM32F103) | Pin Function | Connect To (USB‑TTL/ESP32) | Purpose |
| :---: | :---: | :---: | :---: |
| **PA9** | **USART1_TX** (Transmit) | **USB‑TTL RX** (Receive) | Send data to PC terminal |
| **PA10** | **USART1_RX** (Receive) | **USB‑TTL TX** (Transmit) | PC terminal control (rarely used) |
| **PA0** | **ADC1_IN0** | **ESP32 GPIO 25 (DAC1)** | Receive analog input |
| **PA1** | **ADC1_IN1** | **ESP32 GPIO 26 (DAC2)** | Receive analog input |
| **GND** | **Ground** | **USB‑TTL/ESP32 GND** | **Must share common ground** |

---

### 3. 🛠️ Step‑by‑Step Implementation Guide

#### Step 1: [_STM32CubeMX Configuration (Hardware Framework)_](./CubeMX_Setting.pdf)

1. **MCU Selection:** Choose `STM32F103C8Tx`.
2. **Clock Source:** Enable HSE (external crystal). If using ST‑Link, select SWD debugging.
3. **Peripheral Configuration:**
   - **ADC1:** Enable **IN0 (PA0)**, **IN1 (PA1)**, **IN2 (PA2)**.  
     Set **Continuous Conversion Mode: Enabled** and **Scan Conversion Mode: Enabled**.
   - **DMA:** Enable DMA request for ADC1, set mode to **Circular**, direction **Peripheral to Memory**.
   - **USART1:** Set **Mode: Asynchronous**, **Baud Rate: 115200**.
4. **Clock Tree:**  
   Ensure ADC Clock (`PCLK2`) is around **14 MHz**  
   (commonly `72 MHz / 6 = 12 MHz` or `72 MHz / 8 = 9 MHz`) for accurate sampling.
5. **Generate code** and import into your IDE.

---

#### Step 2: [_Code Logic Implementation (main.c)_](./STM32F103_Code.c)

1. **Variable Declaration:**  
   Declare the DMA buffer in `/* USER CODE BEGIN Includes */` or globally.
   ```c
   #define NUM_ADC_CHANNELS 3
   uint16_t adc_buffer[NUM_ADC_CHANNELS];
   ```
2. **Start DMA:**  
   In `/* USER CODE BEGIN 2 */`, start ADC calibration and DMA transfer.
   ```c
   HAL_ADCEx_Calibration_Start(&hadc1); 
   HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer, NUM_ADC_CHANNELS);
   char *boot_msg = "!!! UART Test Success. Starting ADC Loop... !!!\r\n";
   HAL_UART_Transmit(&huart1, (uint8_t*)boot_msg, strlen(boot_msg), 1000);
   ```
3. **Main Loop (while(1)):**  
   Read the buffer and output via UART.
   - Use **millivolt integer calculations** for stability (as in the final version).

---

#### Step 3: Signal Source & Testing (Verification)

1. [_**ESP32 Flashing:**_](./ESP32_Code.cpp)  
   Flash the DAC waveform generator code and connect signal lines to PA0 and PA1.
2. **STM32 Flashing:**  
   Flash the final `main.c` firmware.
3. **Terminal Monitoring:**  
   Open a PC terminal at **115200 baud** and observe whether the data updates continuously and regularly.

---

### 4. ❓ Q&A / Troubleshooting

| Issue (Symptom) | Root Cause | Solution |
| :---: | :---: | :---: |
| **No output on terminal** | UART wiring error or program stuck. | 1. Check if **RX/TX** are reversed (most common).<br>2. Ensure **GND** is shared.<br>3. Send a simple message **before** `HAL_ADC_Start_DMA` to isolate the issue. |
| **Garbled output** | Baud rate mismatch. | Ensure CubeMX (`115200`) and PC terminal settings match **exactly**. |
| **Only ADC values shown, voltage field blank** | `sprintf` floating‑point support disabled. | Use **millivolt (mV) integer calculations** (final project solution). |
| **ADC data not changing or frozen** | Continuous Conversion Mode or Circular DMA not enabled. | Check CubeMX: both must be **Enabled / Circular**. |
| **PC13 LED blinking rapidly** | Program entered `Error_Handler()`. | Check return value of `HAL_ADC_Start_DMA`, or verify peripheral initialization such as `MX_GPIO_Init()`. |