// -----------------------------------------------------------------
// Edge-AI Smart Sorting PoC: Step 2 (Final Sensor + Classification Logic - COMPILE FIX)
// Focus: Corrected usage of global variables (red_light, green_light, blue_light) 
//        in the decision logic state.
// -----------------------------------------------------------------

// --- 1. HX711 (Load Cell Module) ---
#include "HX711_ADC.h"
const int HX711_DAT_PIN = 33; 
const int HX711_CLK_PIN = 32; 
HX711_ADC LoadCell(HX711_DAT_PIN, HX711_CLK_PIN);
const float CALIBRATION_FACTOR = 50.4; 


// --- 2. APDS-9960 色彩與接近偵測模組 ---
#include <Wire.h> 
#include <SparkFun_APDS9960.h>

SparkFun_APDS9960 apds = SparkFun_APDS9960();

// --- 3. OLED 螢幕模組 (I2C) ---
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define OLED_RESET -1         
#define SCREEN_WIDTH 128      
#define SCREEN_HEIGHT 64      
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET); 

// --- 全域變數用於感測器讀數與結果 ---
uint16_t ambient_light = 0;
uint16_t red_light = 0;
uint16_t green_light = 0;
uint16_t blue_light = 0;
uint8_t proximity_value = 0;

float currentWeight = 0.0;
float finalWeight = 0.0; 
String classificationResult = "PENDING"; 


// --- 狀態機定義 ---
enum TestState {
  STATE_IDLE,             
  STATE_WEIGHT_READING,   
  STATE_WAIT_FOR_MOVE,    
  STATE_COLOR_READING,    
  STATE_DECISION_READY    
};
TestState currentState = STATE_IDLE; 

// --- 閾值定義 ---
const float WEIGHT_THRESHOLD = 2.0;       
const uint8_t PROXIMITY_COLOR_THRESHOLD = 50; 

// 分類閾值
const float CLASSIFY_WEIGHT_THRESHOLD = 50.0; 
const float RED_RATIO_THRESHOLD = 1.2;       


// --- 數據穩定變數 (核心) ---
float weightAccumulator = 0.0;
int weightReadingsTaken = 0;
const int WEIGHT_STABILITY_COUNT = 15; 

uint32_t redAccumulator = 0;
uint32_t greenAccumulator = 0;
uint32_t blueAccumulator = 0;

int colorReadingsTaken = 0;
const int COLOR_STABILITY_COUNT = 25; 
const int COLOR_BURN_IN_COUNT = 5;    

bool colorBurnInComplete = false;
int burnInCounter = 0;


// ====================================================================

void setup() {
  Serial.begin(115200);
  Serial.println("--- PoC System Initialization ---");

  // I2C 初始化 (GPIO 21/22)
  Wire.begin(21, 22); 

  // OLED 初始化
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("OLED 啟動失敗!")); while (true); 
  } else {
    display.clearDisplay(); display.setTextSize(1); display.setTextColor(SSD1306_WHITE); display.setCursor(0,0);
    display.println("OLED Ready!"); display.display();
  }
  
  // --- APDS-9960 初始化 (最終穩定配置：只使用環境光) ---
  if (apds.init()) {
    
    if (apds.enableLightSensor(false)) { 
      if (!apds.setAmbientLightGain(APDS9960_GCONF4)) { 
        Serial.println("Warning: 無法設定 Ambient Light Gain.");
      }
    }
    
    if (!apds.enableProximitySensor(false)) {
         Serial.println("Warning: 無法啟用 Proximity Sensor.");
    }
    
  } else {
    Serial.println("APDS-9960 啟動失敗!");
  }


  // HX711 初始化與 Tare
  LoadCell.begin(); LoadCell.start(200); LoadCell.setSamplesInUse(1); LoadCell.powerUp();     
  Serial.println("Performing Tare (Zeroing)...");
  LoadCell.tare(); 
  LoadCell.setCalFactor(CALIBRATION_FACTOR);
  delay(500); 
  
  Serial.println("-------------------------------------");
  Serial.println("PoC SENSOR LAYER READY! Starting State Machine.");
  Serial.println("-------------------------------------");
}

void loop() {
  
  // 1. 讀取所有感測器數據 (同步讀取)
  if (LoadCell.update()) {
    currentWeight = LoadCell.getData() / CALIBRATION_FACTOR;
  }
  apds.readAmbientLight(ambient_light);
  apds.readRedLight(red_light);
  apds.readGreenLight(green_light);
  apds.readBlueLight(blue_light);
  apds.readProximity(proximity_value); 
  
  // 2. 狀態機邏輯處理
  switch (currentState) {
    
    case STATE_IDLE:
      if (currentWeight > WEIGHT_THRESHOLD) {
        weightAccumulator = 0.0;
        weightReadingsTaken = 0;
        classificationResult = "PENDING"; 
        currentState = STATE_WEIGHT_READING;
        Serial.println("-> State Change: WEIGHT_READING (Object detected, starting stabilization).");
      }
      break;

    case STATE_WEIGHT_READING:
      if (currentWeight > WEIGHT_THRESHOLD) {
        weightAccumulator += currentWeight;
        weightReadingsTaken++;
        
        if (weightReadingsTaken >= WEIGHT_STABILITY_COUNT) {
            finalWeight = weightAccumulator / WEIGHT_STABILITY_COUNT;
            
            Serial.printf("-> Weight Locked (Avg. of %d): %.2fg. Please move object to the Color Station.\n", WEIGHT_STABILITY_COUNT, finalWeight);
            
            weightAccumulator = 0.0;
            weightReadingsTaken = 0;

            currentState = STATE_WAIT_FOR_MOVE;
        }
      } else {
        Serial.println("-> Warning: Object removed from scale prematurely. Resetting to IDLE.");
        currentState = STATE_IDLE;
      }
      break;

    case STATE_WAIT_FOR_MOVE:
      if (proximity_value > PROXIMITY_COLOR_THRESHOLD) {
        redAccumulator = 0; greenAccumulator = 0; blueAccumulator = 0;
        colorReadingsTaken = 0;
        colorBurnInComplete = false;
        burnInCounter = 0;
        
        currentState = STATE_COLOR_READING;
        Serial.println("-> State Change: COLOR_READING (Object detected, starting stabilization with burn-in).");
      }
      break;
      
    case STATE_COLOR_READING:
      if (proximity_value > PROXIMITY_COLOR_THRESHOLD) {
        
        if (!colorBurnInComplete) {
          burnInCounter++;
          if (burnInCounter >= COLOR_BURN_IN_COUNT) {
            colorBurnInComplete = true;
            Serial.printf("   [Color] Burn-in complete (%d readings discarded). Starting averaging...\n", COLOR_BURN_IN_COUNT);
          } else {
            Serial.print(".");
          }
          
        } else {
          redAccumulator += red_light;
          greenAccumulator += green_light;
          blueAccumulator += blue_light;
          colorReadingsTaken++;

          if (colorReadingsTaken >= COLOR_STABILITY_COUNT) {
              uint16_t finalRed = redAccumulator / COLOR_STABILITY_COUNT;
              uint16_t finalGreen = greenAccumulator / COLOR_STABILITY_COUNT;
              uint16_t finalBlue = blueAccumulator / COLOR_STABILITY_COUNT;

              // 將平均值寫入全域變數 (red_light, green_light, blue_light)
              red_light = finalRed;
              green_light = finalGreen;
              blue_light = finalBlue;

              Serial.printf("\n-> Color Locked (Avg. of %d): R:%d, G:%d, B:%d. Data Collection Complete.\n", COLOR_STABILITY_COUNT, finalRed, finalGreen, finalBlue);
              Serial.println("\n--- CLASSIFICATION DATA READY ---");
              Serial.printf("FINAL DATA: Weight=%.2fg, R=%d, G=%d, B=%d\n", finalWeight, red_light, green_light, blue_light);

              currentState = STATE_DECISION_READY;
          }
        }
      } else {
        Serial.println("\n-> Warning: Object removed from color sensor prematurely. Returning to WAIT_FOR_MOVE.");
        currentState = STATE_WAIT_FOR_MOVE;
      }
      break;
      
    case STATE_DECISION_READY:
      
      // 【修正點】：使用全域變數 red_light, green_light, blue_light
      if (classificationResult == "PENDING") {
          
          if (finalWeight >= CLASSIFY_WEIGHT_THRESHOLD) {
              classificationResult = "CLASS A (Heavy)";
          } 
          // R 必須比 G 高 1.2 倍，且 R 必須比 B 高
          else if (red_light > (green_light * RED_RATIO_THRESHOLD) && red_light > blue_light) {
              classificationResult = "CLASS B (Light Red)";
          } 
          // 剩下的都歸類為 C
          else {
              classificationResult = "CLASS C (Light Other)";
          }
          
          Serial.printf("-> CLASSIFICATION RESULT: %s\n", classificationResult.c_str());
          Serial.println("--- Waiting for object removal for next cycle ---");
      }
      
      // 等待物體完全移開，然後重置到 IDLE
      if (proximity_value < 30 && currentWeight < 1.0) {
        Serial.println("\n--- Cycle Complete. System Resetting. ---\n");
        currentState = STATE_IDLE; 
        finalWeight = 0.0;
        classificationResult = "PENDING"; 
      }
      break;
  }
  
  // 3. 顯示數據 (OLED Screen) 
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("STATUS: "); 
  
  switch (currentState) {
    case STATE_IDLE: display.println("IDLE"); break;
    case STATE_WEIGHT_READING: display.printf("1/2 WEIGHT (%d/%d)", weightReadingsTaken, WEIGHT_STABILITY_COUNT); break;
    case STATE_WAIT_FOR_MOVE: display.println(">> MOVE"); break;
    case STATE_COLOR_READING: 
        if (!colorBurnInComplete) {
            display.printf("2/2 BURN-IN (%d/%d)", burnInCounter, COLOR_BURN_IN_COUNT);
        } else {
            display.printf("2/2 COLOR (%d/%d)", colorReadingsTaken, COLOR_STABILITY_COUNT);
        }
        break;
    case STATE_DECISION_READY: display.println("DECIDE!"); break;
  }
  
  display.setCursor(0, 14);
  display.print("W_Lock:"); display.print(finalWeight, 2); display.print("g");
  display.print(" P:"); display.println(proximity_value);
  
  display.setCursor(0, 28);
  display.print("R/G/B:"); 
  display.print(red_light); display.print("/"); 
  display.print(green_light); display.print("/"); 
  display.println(blue_light);
  
  display.setCursor(0, 42);
  display.print("W_Live:"); display.print(currentWeight, 2); display.print("g");

  display.setCursor(0, 56);
  display.print("RESULT: "); 
  if (currentState == STATE_DECISION_READY) {
     display.println(classificationResult); 
  } else {
     display.println("Pending..."); 
  }
  
  display.display();
  
  delay(100); 
}