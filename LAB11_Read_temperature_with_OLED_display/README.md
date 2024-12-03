# Read temperature with OLED display

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

# Code
* use temperature sensor function to read the value
* make sure MCU type support sensor, and install "Adafruit_GFX.h" and "Adafruit_SSD1306.h" for OLED
* define text format, like size, color, coordination
* string required to print on OLED

```C++
//define termperature sensor function
#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read();
#ifdef __cplusplus
}
#endif
uint8_t temprature_sens_read();

#include <Wire.h>
//OLED display
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define CREEN_WIDTH 128 		//set OLED display width
#define CREEN_HEIGHT 64  		//set OLED display height
Adafruit_SSD1306 display(CREEN_WIDTH, CREEN_HEIGHT, &Wire); 		//define I2C for OLED

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  if(!display.begin(SSD1306_SWITCHCAPVCC,0x3C)) { 		//address at 0x3c, and initialize
    Serial.println(F("SSD1306 allocation falled"));		   
    for(;;); // Don't proceed, loop forever
  }
  display.clearDisplay(); 		//clear display
}

void loop() {
  // put your main code here, to run repeatedly:
  // Convert raw temperature in F to Celsius degrees
  float degree_in_Celsius = (temprature_sens_read()-32)/1.8;

  //on OLED
  //text format: size, color, coordination
  display.setTextSize(1); 
  display.setTextColor(1);
  display.setCursor(0,0);
  //string to be shown
  display.print("Temperature: ");

  //text format: size, color, coordination
  display.setTextSize(2); 
  display.setTextColor(1);
  display.setCursor(20,30);
  //string to be shown
  display.print(degree_in_Celsius);
  display.print(" C");

  display.display(); 		//print on OLED
  delay(5000);
}
```
