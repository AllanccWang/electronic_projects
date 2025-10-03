# electronic_projects
implement the circuit with microcontroller

# 🔧 Project Index (Sorted by LAB Number)
- [LAB1_RC_circuit/](LAB1_RC_circuit/) — Updated: Sun Oct 6 13:49:45 2024 +0800
- [LAB2_Analog_Input_Voltage/](LAB2_Analog_Input_Voltage/) — Updated: Sun Oct 6 13:46:23 2024 +0800
- [LAB3_binary_display_with_LED/](LAB3_binary_display_with_LED/) — Updated: Wed Oct 2 20:02:37 2024 +0800
- [LAB4_Photoresistor_switch_circuit/](LAB4_Photoresistor_switch_circuit/) — Updated: Sun Oct 6 13:48:12 2024 +0800
- [LAB5_Planck_constant_experiment/](LAB5_Planck_constant_experiment/) — Updated: Sun Oct 6 16:32:43 2024 +0800
- [LAB6_ESP32_Based_Real_Time_Oscilloscope/](LAB6_ESP32_Based_Real_Time_Oscilloscope/) — Updated: Sat Oct 19 14:57:18 2024 +0800
- [LAB7_ESP32_as_WIFI_Station/](LAB7_ESP32_as_WIFI_Station/) — Updated: Sun Oct 27 14:30:20 2024 +0800
- [LAB8_R-2R_resistive_ladder/](LAB8_R-2R_resistive_ladder/) — Updated: Sat Nov 9 17:29:12 2024 +0800
- [LAB9_ESP32_WebServer_control_Two_LEDs/](LAB9_ESP32_WebServer_control_Two_LEDs/) — Updated: Wed Nov 27 15:35:01 2024 +0800
- [LAB10_ESP32_WebServer_slider_control_LED_PWM/](LAB10_ESP32_WebServer_slider_control_LED_PWM/) — Updated: Thu Nov 28 18:37:38 2024 +0800
- [LAB11_Read_temperature_with_OLED_display/](LAB11_Read_temperature_with_OLED_display/) — Updated: Tue Dec 3 16:44:35 2024 +0800
- [LAB12_practice_on_APDS9960_sensor/](LAB12_practice_on_APDS9960_sensor/) — Updated: Sat Dec 14 18:43:50 2024 +0800
- [LAB13_555Timer_Function_Table_Test/](LAB13_555Timer_Function_Table_Test/) — Updated: Sat Jan 4 17:57:16 2025 +0800
- [LAB14_Verify_P2N2222A_Amplifier-Transistor_Switching/](LAB14_Verify_P2N2222A_Amplifier-Transistor_Switching/) — Updated: Thu Oct 2 15:31:22 2025 +0800
- [LAB15_P2N2222A-Amplifier-Transistor_voltage_validation/](LAB15_P2N2222A-Amplifier-Transistor_voltage_validation/) — Updated: Fri Oct 3 17:07:07 2025 +0800

# pinout of micorcontroller, ESP32
<img align="justify" src="ESP32-WeMos-LOLIN-D32-pinout.jpg" alt="CG" style="width:80%">

# specs
* Processors:
  * CPU: Xtensa dual-core (or single-core) 32-bit LX6 microprocessor, operating at 160 or 240 MHz and performing at up to 600 DMIPS
  * Ultra low power (ULP) co-processor
* Memory: 520 KiB SRAM
* Wireless connectivity:
  * Wi-Fi: 802.11 b/g/n
  * Bluetooth: v4.2 BR/EDR and BLE (shares the radio with Wi-Fi)
* Peripheral interfaces:
  * 12-bit SAR ADC up to 18 channels
  * 2 × 8-bit DACs
  * 10 × touch sensors (capacitive sensing GPIOs)
  * 4 × SPI
  * 2 × I²S interfaces
  * 2 × I²C interfaces
  * 3 × UART
  * SD/SDIO/CE-ATA/MMC/eMMC host controller
  * SDIO/SPI slave controller
  * Ethernet MAC interface with dedicated DMA and IEEE 1588 Precision Time Protocol support
  * CAN bus 2.0
  * Infrared remote controller (TX/RX, up to 8 channels)
  * Motor PWM
  * LED PWM (up to 16 channels)
  * Hall effect sensor
  * Ultra low power analog pre-amplifier
* Security:
  * IEEE 802.11 standard security features all supported, including WFA, WPA/WPA2 and WAPI
  * Secure boot
  * Flash encryption
  * 1024-bit OTP, up to 768-bit for customers
  * Cryptographic hardware acceleration: AES, SHA-2, RSA, elliptic curve cryptography (ECC), random number generator (RNG)
* Power management:
  * Internal low-dropout regulator
  * Individual power domain for RTC
  * 5μA deep sleep current
  * Wake up from GPIO interrupt, timer, ADC measurements, capacitive touch sensor interrupt
* Battery management
  * Connector for 3.7v battery (like 18650).
