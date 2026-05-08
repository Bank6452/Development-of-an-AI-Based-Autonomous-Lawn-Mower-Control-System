#include <Arduino.h>
#include "ultrasonic.h"

void setup() {
  Serial.begin(115200);
  Serial.println("--- ESP32 Ultrasonic Hub (2-Sensor Mode: L/R) ---");

  initUltrasonic();
  
  Serial.println("🚀 Ready to monitor Left and Right Sonars!");
}

void loop() {
  // 📡 อ่านค่าเฉพาะซ้ายและขวา
  float uLeft, uRight;
  readUltrasonic(uLeft, uRight);
  
  // ⚡ ส่งแค่ 2 ค่า: ซ้าย,ขวา
  Serial.print("U,");
  Serial.print(uLeft, 1); Serial.print(",");
  Serial.println(uRight, 1);

  delay(50); 
}
