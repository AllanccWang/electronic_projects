# R-2R resistive ladder

practice on a R-2R resistive ladder DAC circuit. R-2R resistive ladder provides a simple means of converting digital voltage signals into an equivalent analogue output.
refer to : [LINK](https://www.electronics-tutorials.ws/combination/r-2r-dac.html) and [LINK](https://www.instructables.com/R2R-Digital-Analog-Converter-DAC/)

# Components
* Arduino UNO
* Breadboard
* wires
* 6 unit of 2kΩ
* 4 unit of 1kΩ
* oscilloscope

# Software
* [Tinkercad](https://www.tinkercad.com/) : Arduino UNO

# Simulation
* [**_R-2R resistive ladder_**](https://www.tinkercad.com/things/jH8VCkvaYPu-r-2r-resistive-ladder?sharecode=AEccUuROgGydeU4dj-gq7G51oSW0cNwep27xJXzuztE)

# Code
```C++
uint8_t level = 0;

void setup()
{
DDRD = B01111100; // set all Digital Pins on PORTD to OUTPUT
}

void loop()
{
  //Rectangle
  //PORTD = 124;  // 124 is 01111100 in binary
  //delay(1);
  //PORTD = 0;	// 0 is 00000000 in binary
  //delay(1);
  
  //Sawtooth
  level %= 124;
  PORTD = level++;
  
  //Triangle
  //for(int i = -124 ; i < 124 ; i++){
  //PORTD = abs(i);
  //}
}
```
