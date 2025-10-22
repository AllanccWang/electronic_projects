// -----------------------------------------------------------------
// Edge-AI Smart Sorting : FINAL STABLE CODE (Manual Pulse Generation)
// Focus: Bypassing all Servo/LEDC library issues with direct digital pulse control.
// -----------------------------------------------------------------

// --- 1. HX711 (Load Cell Module) ---
#include "HX711_ADC.h"
const int HX711_DAT_PIN = 33; 
const int HX711_CLK_PIN = 32; 
HX711_ADC LoadCell(HX711_DAT_PIN, HX711_CLK_PIN);
const float CALIBRATION_FACTOR = 50.4; 


// --- 2. APDS-9960 Color and Proximity Sensor Module ---
#include <Wire.h> 
#include <SparkFun_APDS9960.h>
SparkFun_APDS9960 apds = SparkFun_APDS9960();

// --- 3. OLED Screen Module (I2C) ---
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define OLED_RESET -1         
#define SCREEN_WIDTH 128      
#define SCREEN_HEIGHT 64      
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET); 

// --- 4. Actuator Layer Module (Using Manual Pulse Generation) ---
const int SERVO_PIN = 25;  // Servo Motor connected to GPIO25
const int BUZZER_PIN = 26; // Buzzer connected to GPIO26

// SG90 Pulse Width Definition (Unit: microseconds us)
const int PULSE_MIN_US = 500;   // Approx. 0 degrees
const int PULSE_MID_US = 1500;  // Approx. 90 degrees
const int PULSE_MAX_US = 2500;  // Approx. 180 degrees
const int FRAME_TIME_MS = 20;   // 20ms period (50Hz)


// --- Global Variables for Sensor Readings and Results ---
uint16_t ambient_light = 0;
uint16_t red_light = 0;
uint16_t green_light = 0;
uint16_t blue_light = 0;
uint8_t proximity_value = 0;

float currentWeight = 0.0;
float finalWeight = 0.0; 
String classificationResult = "PENDING"; 

bool actuationExecuted = false; 


// --- State Machine Definition ---
enum TestState {
  STATE_IDLE,             
  STATE_WEIGHT_READING,   
  STATE_WAIT_FOR_MOVE,    
  STATE_COLOR_READING,    
  STATE_DECISION_READY    
};
TestState currentState = STATE_IDLE; 

// --- Threshold Definitions ---
const float WEIGHT_THRESHOLD = 2.0;       
const uint8_t PROXIMITY_COLOR_THRESHOLD = 50; 

// Classification Thresholds
const float CLASSIFY_WEIGHT_THRESHOLD = 50.0; 
const float RED_RATIO_THRESHOLD = 1.2;       


// --- Data Stabilization Variables (Core) ---
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

// [Manual Pulse Generation Function]: Simulates Servo.write(angle)
void manualServoWrite(int angle) {
  // Linearly map 0-180 degrees to 500us to 2500us
  int pulseWidth_us = map(angle, 0, 180, PULSE_MIN_US, PULSE_MAX_US);
  
  // Servo motors require continuous pulses to maintain position. We send one pulse every 20ms (50Hz).
  // In loop(), we only need to call this function once to set the angle, assuming loop() is fast enough to update continuously.
  // For safety, we send several continuous pulses during decision execution to ensure the motor reaches the position.

  // Note: Since we cannot use delay() in loop(), this function only calculates the pulse width.
  // The actual pulse sending will be performed in the actuationExecuted block.
  // We use a global variable to save the current pulse width.

  // Note: This method is difficult to implement perfectly in a single-threaded loop(), but sufficient for brief sorting.
  
  // For this test, we will call this pulse generation logic in the setup and DECIDE state.
}

void setup() {
  Serial.begin(115200);
  Serial.println("--- PoC System Initialization ---");

  // I2C Initialization (GPIO 21/22)
  Wire.begin(21, 22); 

  // --- Actuator Layer Setup ---
  pinMode(BUZZER_PIN, OUTPUT);    // Set Buzzer Pin as output
  
  // [Servo Pin Setup]: Set as output only
  pinMode(SERVO_PIN, OUTPUT);
  
  // Set to 0 degrees (Home Position) on startup
  for (int i = 0; i < 50; i++) { // Send 50 pulses to ensure zeroing
    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(PULSE_MIN_US); // 500 us
    digitalWrite(SERVO_PIN, LOW);
    delay(FRAME_TIME_MS); // Delay 20ms
  }
  Serial.println("Servo Home Position (0 deg) Set.");


  // OLED Initialization
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("OLED Startup Failed!")); while (true); 
  } else {
    display.clearDisplay(); display.setTextSize(1); display.setTextColor(SSD1306_WHITE); display.setCursor(0,0);
    display.println("OLED Ready!"); display.display();
  }
  
  // APDS-9960 Initialization (Use ambient light only)
  if (apds.init()) {
    if (apds.enableLightSensor(false)) { 
      if (!apds.setAmbientLightGain(APDS9960_GCONF4)) { 
        Serial.println("Warning: Could not set Ambient Light Gain.");
      }
    }
    if (!apds.enableProximitySensor(false)) {
         Serial.println("Warning: Could not enable Proximity Sensor.");
    }
  } else {
    Serial.println("APDS-9960 Startup Failed!");
  }

  // HX711 Initialization and Tare
  LoadCell.begin(); LoadCell.start(200); LoadCell.setSamplesInUse(1); LoadCell.powerUp();     
  Serial.println("Performing Tare (Zeroing)...");
  LoadCell.tare(); 
  LoadCell.setCalFactor(CALIBRATION_FACTOR);
  delay(500); 
  
  Serial.println("-------------------------------------");
  Serial.println("PoC SENSOR LAYER READY! Starting State Machine.");
  Serial.println("-------------------------------------");
}

// Buzzer Control Function
void playClassTone(String classification) {
    if (classification == "CLASS A (Heavy)") {
        tone(BUZZER_PIN, 1000, 200); // High frequency (1000 Hz, 200 ms)
    } else if (classification == "CLASS B (Light Red)") {
        tone(BUZZER_PIN, 500, 200);  // Medium frequency (500 Hz, 200 ms)
    } else { // CLASS C
        tone(BUZZER_PIN, 250, 200);  // Low frequency (250 Hz, 200 ms)
    }
}


// [NEW]: Servo Motor Execution Function - Called in DECISION_READY
void executeServoAction(int angle) {
  int pulseWidth_us;
  
  if (angle == 180) {
    pulseWidth_us = PULSE_MAX_US;
  } else if (angle == 90) {
    pulseWidth_us = PULSE_MID_US;
  } else { // 0 degrees
    pulseWidth_us = PULSE_MIN_US;
  }

  // Send 50 continuous pulses to drive the SG90 to the specified position
  for (int i = 0; i < 50; i++) {
    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(pulseWidth_us); 
    digitalWrite(SERVO_PIN, LOW);
    // Delay for total 20ms - pulse width
    delay(FRAME_TIME_MS); 
  }
}


void loop() {
  
  // 1. Read all sensor data (Synchronous read)
  if (LoadCell.update()) {
    currentWeight = LoadCell.getData() / CALIBRATION_FACTOR;
  }
  apds.readAmbientLight(ambient_light);
  apds.readRedLight(red_light);
  apds.readGreenLight(green_light);
  apds.readBlueLight(blue_light);
  apds.readProximity(proximity_value); 
  
  // 2. State Machine Logic Processing
  switch (currentState) {
    
    case STATE_IDLE:
      if (currentWeight > WEIGHT_THRESHOLD) {
        weightAccumulator = 0.0;
        weightReadingsTaken = 0;
        classificationResult = "PENDING"; 
        actuationExecuted = false; 
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
      
      if (classificationResult == "PENDING") {
          
          if (finalWeight >= CLASSIFY_WEIGHT_THRESHOLD) {
              classificationResult = "CLASS A (Heavy)";
          } 
          else if (red_light > (green_light * RED_RATIO_THRESHOLD) && red_light > blue_light) {
              classificationResult = "CLASS B (Light Red)";
          } 
          else {
              classificationResult = "CLASS C (Light Other)";
          }
          
          Serial.printf("-> CLASSIFICATION RESULT: %s\n", classificationResult.c_str());
          Serial.println("--- Waiting for object removal for next cycle ---");
      }

      // [Actuation Execution Block]: Executes only once after decision
      if (actuationExecuted == false) {
          
          if (classificationResult == "CLASS A (Heavy)") {
              executeServoAction(180); // Class A: 180 degrees
          } else if (classificationResult == "CLASS B (Light Red)") {
              executeServoAction(90);  // Class B: 90 degrees
          } else {
              executeServoAction(0);   // Class C: 0 degrees
          }
          
          playClassTone(classificationResult); // Play confirmation tone
          actuationExecuted = true;
          
      }
      
      // Self-Reset Logic (using corrected thresholds)
      if (proximity_value < 30 && currentWeight < 5.0) { 
        Serial.println("\n--- Cycle Complete. System Resetting. ---");
        executeServoAction(0); // Ensure servo motor returns to Home Position (0 degrees)
        noTone(BUZZER_PIN);    // Stop buzzer (if still sounding)
        currentState = STATE_IDLE; 
        finalWeight = 0.0;
        classificationResult = "PENDING"; 
        actuationExecuted = false; 
      }
      break;
  }
  
  // 3. Display Data (OLED Screen) 
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("STATUS: "); 
  
  switch (currentState) {
    case STATE_IDLE: display.println("IDLE"); break;
    case STATE_WEIGHT_READING: display.printf("1/2 W (%d/%d)", weightReadingsTaken, WEIGHT_STABILITY_COUNT); break;
    case STATE_WAIT_FOR_MOVE: display.println(">> MOVE"); break;
    case STATE_COLOR_READING: 
        if (!colorBurnInComplete) { display.printf("2/2 BURN-IN (%d/%d)", burnInCounter, COLOR_BURN_IN_COUNT); } 
        else { display.printf("2/2 COLOR (%d/%d)", colorReadingsTaken, COLOR_STABILITY_COUNT); }
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