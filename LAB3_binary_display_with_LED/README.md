# Binary Display with LED

use 4 different color LEDs to display the binary representation of number from 0 to 15, less than 2^4 combination

# Components
* Arduino UNO
* Breadboard
* wires
* 4 unit of LED
* 4 unit of 220Ω

# Software
* [WOKWI Simulator](https://wokwi.com/) : Arduino UNO

# Simulation
* [**_Binary Display with LED_**](https://wokwi.com/projects/410633547969555457)

# Code
```C++
void setup() {
  // put your setup code here, to run once:
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  for(int num=0;num<16;num++){
    //Function that convert Decimal to binary
    for(int i = 3; i >= 0; i--){
        int k = num>>i;
        if(i == 3)//MSB : LED yellow
          digitalWrite(13, (k&1)?HIGH:LOW);
        if(i == 2)
          digitalWrite(12, (k&1)?HIGH:LOW);
        if(i == 1)
          digitalWrite(11, (k&1)?HIGH:LOW);
        if(i == 0)//LSB : LED red
          digitalWrite(10, (k&1)?HIGH:LOW);
    }
    delay(2000);
  }
}
```
