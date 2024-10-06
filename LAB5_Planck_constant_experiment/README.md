# Planck constant experiment
in this lab, we use threshold voltage of Red LED to determine the Planck constant. [(Reference)](https://ncmn.unl.edu/outreach/Home_Resources/PlanckAnnotations.pdf)

<img align="justify" src="Planck_constant_measurement.jpg" alt="PlanckCM" style="width:50%">

# Components
* ESP32 WeMos LOLIN D32
* USB
* Breadboard
* wires
* 1 unit of LED
* 1 unit of 220Ω
* 1 unit of 2.2kΩ
* 1 unit of CdS photoresistor

# Software
* IDE: Arduino IDE
* Python module: PySerial [(Reference)](https://www.instructables.com/Capture-Data-From-Arduino-to-CSV-File-Using-PySeri/)

# Wiring
after setup the circuit, using a shelter to cover the LED and photoresistor is used to avoid other light resource affects the reading voltage value from photoresistor
<img align="justify" src="practice_Planck_constant_measurement.jpg" alt="PlanckCM1" style="width:60%">



# Code
* use GPIO5 as a power source
* push switcher to see if RC circuit lights up LED, and LED light will fade as capacitor discharging

```C++
int DAC1_pin = 25; //control LED voltage
int ADC_pin = 26; //read the photoresistor voltage

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(DAC1_pin, OUTPUT);
  dacWrite(DAC1_pin, 0);
  delay(1500);
}

int desired_voltage=1500;
void loop() {
  // put your main code here, to run repeatedly:
  int dac_value = map(desired_voltage, 0, 3300, 0, 255);
  //LED voltage(mV)
  dacWrite(DAC1_pin, dac_value);
  delay(4000);

  //read photoresistor voltage(mV)
  int adc_value=analogRead(ADC_pin);
  delay(1000);

  Serial.print(desired_voltage);
  Serial.print(",");
  Serial.println((int)(adc_value*3300)/4095);
  delay(500);
  desired_voltage+=20;

  if(desired_voltage>1920)
    desired_voltage=1500;
    delay(3000);
}
```
