# Read_temperature_with_OLED_display

read ESP32 internal temperature sensor, and display value on OLED

# Components
* ESP32 WeMos LOLIN D32
* USB
* Breadboard
* wires
* 1 unit of OLED

# Software
* IDE: Arduino IDE with lib, "Adafruit_GFX.h" and "Adafruit_SSD1306.h"

# Wiring
<img align="justify" src="Read_temperature_with_OLED_display.jpg" alt="ReadTemp_OLED" style="width:80%">
| OLED | description | ESP32 |
| ---- | ----------- | --- |
| VCC  | power | 3V |
| GND  | ground | GND |
| SDA  | I2C data | 21 |
| SCL  | I2C clock | 22 |
