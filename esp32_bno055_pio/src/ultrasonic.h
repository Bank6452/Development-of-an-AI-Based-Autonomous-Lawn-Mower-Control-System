#ifndef ULTRASONIC_H
#define ULTRASONIC_H

#include <Arduino.h>

// 📍 ขา Pin สำหรับ ESP32 (เหลือแค่ซ้าย-ขวา)
#define COMMON_TRIG_PIN 32
#define ECHO_LEFT_PIN   33
#define ECHO_RIGHT_PIN  26

void initUltrasonic();
void readUltrasonic(float &left, float &right);

#endif
