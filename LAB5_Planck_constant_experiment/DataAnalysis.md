# Data Analysis
* Calculation
from the LED1 data below, we find there is a turning point as LED voltage is 1660mV.

<img align="justify" src="imgs/Planck_constant_measurement_img1.jpg" alt="Planckdata1" style="width:70%">

by using a formula, E=hv=eV , it's able to calculate the h, the Planck constant.
where E is energy, v=c/λ (v is light frequenct; c is light speed; λ is wavelength), e is electron charge, V is voltage.

since it's red LED, we assume wavelength is 700nm [(red_LED_datasheet)](LAB5_Planck_constant_experiment/RED_LED_datasheet.pdf). And Planck constant is defined as $6.626*10^{-34}$. below is the table manifests all caculated results for 3 units of red LED.

|      | Voltage (mV) | Energy (E=eV) | Frequency (Hz) | Planck Constant (h) | error (%) |
| ---- | ------------- | ------------- | ------------- | ------------------- | --------- |
| LED1 |   1660  | $2.656*10^{-19}$ | $4.285*10^{14}$ | $6.198*10^{-34}$ | 6.4% |
| LED2 |   1640  | $2.624*10^{-19}$ | $4.285*10^{14}$ | $6.123*10^{-34}$ | 7.5% |
| LED3 |   1640  | $2.624*10^{-19}$ | $4.285*10^{14}$ | $6.123*10^{-34}$ | 7.5% |

all errors, $\frac{experimentValue-definedValue}{definedValue}$(%), are less than 10%.

* Comparision of 3 units of LED
