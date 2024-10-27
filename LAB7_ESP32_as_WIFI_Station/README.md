# ESP32 as WIFI Station

in this practice, ESP32 is configured as Wifi station. When the ESP32 is successfully connected to the WiFi router, the serial port monitor will print out the IP address assigned to the ESP32 and display the connection status information: working mode, Channel, SSID, Passphrase, and BSSID.

<img align="justify" src="ESP32_as_WIFI_Station.png" alt="ESPasWIFI" style="width:40%">

# Components
* ESP32 WeMos LOLIN D32
* USB

# Software
IDE: Arduino IDE

# Code
* import <WiFi.h> module, and set up network name and password
* print the connection information: working mode, Channel, SSID, Passphrase, and BSSID

```C++
#include <WiFi.h> 
const char *ssid     = "********"; //ssid: network name
const char *password = "********"; //pasword：network password

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println(String("Connecting to ")+ssid);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(800);
    Serial.print(".");
  }
  Serial.print("\nIP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("WiFi status:");
  WiFi.printDiag(Serial); //connection information: working mode, Channel, SSID, Passphrase, and BSSID
}
  
void loop() {
}
```
