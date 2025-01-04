# Verify the 555 Timer Function Table

in this practice, it implement the function test on 555 timer with ESP32. here we use NE555P device for this practice, for the device specification, please refer to [**datasheet**](https://datasheet.octopart.com/NE555P-Texas-Instruments-datasheet-7284017.pdf).

<img align="justify" src="555Timer_Function_Table.JPG" alt="555Timer_FuncTable" style="width:80%">

# Components
* ESP32 WeMos LOLIN D32
* USB
* Breadboard
* wires
* 1 unit of NE555P
* 1 unit of RED LED
* 1 unit of 220ohm resistor

# Software
* IDE: Arduino IDE

# Wiring

To verify the output pin, we can use the digitalRead() function to read the value, but for discharge pin, it's connected to LED with 220ohm. As discharge pin is on, it pull to GND, then LED will be on. It's used for validating on/off status of discharge pin.

| NE555P | description | ESP32 |
| ---- | ----------- | --- |
| VCC | power | 3V |
| GND | ground | GND |
| Threshold | input pin | 33 |
| Trigger | input pin | 19 |
| Reset | input pin | 18 |
| Output | output pin | 26 |
<img align="justify" src="practice_555Timer_Function_Table_Test.jpg" alt="prac_555Timer_FuncTable" style="width:80%">

# Code
* simulate the High/Low value per pin on function table above, and check the value of output pin and LED on/off(for discharge pin).
```C++
int pin_Threshold = 33;   // Threshold pin connected to GPIO33
int pin_Trigger = 19;     // Trigger pin connected to GPIO19
int pin_Reset = 18;       // reset pin connected to GPIO18
int pin_out = 26;         // Discharge pin connected to GPIO26

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  //define pin
  pinMode(pin_Threshold, OUTPUT);
  pinMode(pin_Trigger, OUTPUT);
  pinMode(pin_Reset, OUTPUT);
  pinMode(pin_out, INPUT);
  delay(2000);
  //RESET:Low ; Trigger:Irrelevant ; Treshold:Irrelevant ; Dsicharge:ON
  //Output shold be Low == LED OFF
  digitalWrite(pin_Reset, LOW);
  digitalWrite(pin_Trigger, LOW);   //Irrelevant
  digitalWrite(pin_Threshold, LOW); //Irrelevant
  Serial.print("Condition 1; output pin: ");
  Serial.println(digitalRead(pin_out));
  delay(2000);
  //RESET:HIGH ; Trigger<1/3VDD ; Treshold:Irrelevant ; Dsicharge:OFF
  //Output shold be HIGH == LED ON
  digitalWrite(pin_Reset, HIGH);
  digitalWrite(pin_Trigger, LOW);
  digitalWrite(pin_Threshold, LOW); //Irrelevant
  Serial.print("Condition 2; output pin: ");
  Serial.println(digitalRead(pin_out));
  delay(2000);
  //RESET:HIGH ; Trigger>1/3VDD ; Treshold>2/3VDD ; Dsicharge:ON
  //Output shold be Low == LED OFF
  digitalWrite(pin_Reset, HIGH);
  digitalWrite(pin_Trigger, HIGH);
  digitalWrite(pin_Threshold, HIGH);
  Serial.print("Condition 3; output pin: ");
  Serial.println(digitalRead(pin_out));
  delay(2000);
  //RESET:HIGH ; Trigger>1/3VDD ; Treshold<2/3VDD ; Dsicharge:As previously status
  //Output shold be previously status
  digitalWrite(pin_Reset, HIGH);
  digitalWrite(pin_Trigger, HIGH);
  digitalWrite(pin_Threshold, LOW);
  Serial.print("Condition 4; output pin: ");
  Serial.println(digitalRead(pin_out));

  delay(2000);
}

void loop() {
  // put your main code here, to run repeatedly:
}
```
