# 🚀 STM32F103 DMA Data Acquisition and Analysis Project

## 1. 🎯 Project Purpose

| Category | Description |
| :--- | :--- |
| **Technical Goal** | Learn and implement **ADC (Analog-to-Digital Conversion)** working together with **DMA (Direct Memory Access)**, combined with **Timer triggering** for improved stability. |
| **STM32 Core Advantage** | Demonstrate STM32’s strengths in **real-time performance**, **non-blocking data acquisition**, and **stability**, surpassing ESP32’s polling approach. |
| **Experiment Goal** | Achieve continuous high-speed acquisition of channels (PA0, PA1), output data via UART to PC, while keeping CPU load extremely low. |

---

## 2. 📌 Pin Connection

### I. ADC Input and Sensor Connection

| STM32F103C8T6 Pin | Function | Connected Component |
| :--- | :--- | :--- |
| **PA0** | ADC1\_IN0 (Channel 1) | Potentiometer (middle tap) |
| **PA1** | ADC1\_IN1 (Channel 2) | Voltage divider (10kΩ + 2.2kΩ resistors) |
| **3.3V** | Power output | Breadboard VCC |
| **GND** | Ground | Breadboard GND |

### II. Data Output and Debug Connection

| STM32F103C8T6 Pin | Function | Connected To |
| :--- | :--- | :--- |
| **PA9** | USART1\_TX | CP2102 RXD |
| **PA10** | USART1\_RX | CP2102 TXD |
| **GND** | Ground | CP2102 GND |
| **SWDIO/SWCLK** | Debug/Programming | ST-LINK V2 |

---

## 3. 🛠️ Step-by-Step Guide

### Step 1: CubeMX Project Initialization
1. **RCC Clock**: Use HSE (8 MHz), set SYSCLK to 72 MHz.  
2. **GPIO**: Configure PA0, PA1 as Analog; PC13 as Output (LED).

### Step 2: Configure ADC1
- **Scan Conversion Mode**: Enable  
- **Continuous Conversion Mode**: Disable  
- **External Trigger**: Timer 3 TRGO event  
- **Rank Order**: Rank1 → PA0, Rank2 → PA1  
- **Sampling Time**: 55.5 Cycles (to avoid crosstalk)

### Step 3: Configure TIM3
- **Prescaler**: 719  
- **Period (ARR)**: 999  
- **TRGO**: Update Event  
- **MSM bit**: Enable  
→ Generates 100 Hz trigger frequency

### Step 4: Configure DMA
- **DMA1 Channel1** → ADC1  
- **Mode**: Circular  
- **Data Width**: Peripheral = Half Word (16-bit), Memory = Word (32-bit)

### Step 5: Generate Code and Edit `main.c`
- In `/* USER CODE BEGIN 2 */`:
  ```c
  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_dma_buffer, DMA_BUFFER_SIZE);
  HAL_TIM_Base_Start(&htim3);
  ```

### Step 6: Hardware Testing
- **Common Ground**: Ensure external circuit shares GND with STM32.  
- **UART Test**: Verify stable data output.  

---

## 4. 💻 Code (Core Implementation)

### 1. Global Variables (DMA Buffer and Flag)

```c
#define NUM_CHANNELS 3
#define SAMPLES_PER_CHANNEL 50
#define DMA_BUFFER_SIZE (NUM_CHANNELS * SAMPLES_PER_CHANNEL)
uint32_t adc_dma_buffer[DMA_BUFFER_SIZE];
static volatile uint8_t transmit_flag = 0; // volatile ensures visibility in interrupt
```

### 2. main() Startup Sequence

```c
// Start ADC DMA transfer
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_dma_buffer, DMA_BUFFER_SIZE);

// Start Timer Base (trigger ADC)
HAL_TIM_Base_Start(&htim3); 
```

### 3. DMA Conversion Complete Callback

```c
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{
    if (hadc->Instance == ADC1)
    {
        transmit_flag = 1; // Set flag, process data in main loop
    }
}
```

### 4. Main Loop Data Processing and Voltage Conversion

```c
while (1)
{
    if (transmit_flag == 1)
    {
        // Read first stable sample
        uint32_t raw_ch0 = adc_dma_buffer[0];
        
        // Convert to voltage (VREF=3.3V)
        #define VREF 3.3f
        #define MAX_ADC_VALUE 4095.0f
        float voltage_ch0 = ((float)raw_ch0 / MAX_ADC_VALUE) * VREF;

        // Integer-based output (avoid %f in printf)
        int v0_int = (int)(voltage_ch0 * 100.0f);
        int v0_major = v0_int / 100;
        int v0_minor = v0_int % 100;
        
        char msg[80];
        sprintf(msg, "V: PA0=%d.%02dV...\r\n", v0_major, v0_minor);
        HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), 100);

        transmit_flag = 0;
    }
    HAL_Delay(100); // Control output frequency
}
```

---

## 5. ❓ Q&A (Common Issues and Solutions)

| Question | Cause | Solution |
| :--- | :--- | :--- |
| Why is STM32 better than ESP32 here? | ESP32 `analogRead()` requires CPU polling. | STM32 uses DMA, hardware moves data automatically, CPU remains idle. |
| How fast can sampling go? | STM32F103 ADC can reach 1 MSPS. | Even with multi-channel scanning, tens of kHz are achievable. |
| Why use Circular Mode? | Continuous acquisition requires no interruption. | DMA loops back to buffer start automatically. |
| Compile error: `void value not ignored`? | `MX_ADC1_Init()` is a void function. | Remove `if(... != HAL_OK)` check. |
| No UART output? | Hardware wiring or initialization issue. | Isolate and test UART heartbeat. |
| Data unstable or crosstalk? | ADC Rank misconfigured or Sampling Time too short. | Fix Rank, set Sampling Time ≥ 55.5 Cycles. |
| PA0 connected to 3.3V still unstable? | External circuit not sharing ground. | Ensure external power and STM32 share GND. |
| `sprintf` with `%f` error? | STM32 default printf doesn’t support float. | Use integer output method (×100 then split integer/decimal). |