// LOLIN D32 的內建 LED 在 GPIO 5
#define LED_PIN 5 

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("===== LOLIN D32 正式燈號測試 =====");

  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  // 因為 LOLIN D32 是低電位點亮，LOW 反而是「亮」，HIGH 是「滅」
  // digitalWrite(LED_PIN, HIGH);   // 點亮藍色 LED
  // Serial.println("LED 狀態: 亮 (LOW)");
  delay(300);                   // 閃快一點 (0.3秒) 比較明顯

  digitalWrite(LED_PIN, LOW);  // 熄滅 LED
  Serial.println("LED 狀態: 滅 (HIGH)");
  delay(300); 
}