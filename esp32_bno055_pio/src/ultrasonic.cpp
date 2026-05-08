#include "ultrasonic.h"

#define DISTANCE_OFFSET 3.0 

void initUltrasonic() {
    pinMode(COMMON_TRIG_PIN, OUTPUT);
    pinMode(ECHO_LEFT_PIN, INPUT);
    pinMode(ECHO_RIGHT_PIN, INPUT);
    digitalWrite(COMMON_TRIG_PIN, LOW);
}

float getSingleDistance(int echoPin) {
    long duration = 0;
    
    // ลองยิง 2 ครั้ง
    for(int i = 0; i < 2; i++) {
        digitalWrite(COMMON_TRIG_PIN, LOW);
        delayMicroseconds(5);
        digitalWrite(COMMON_TRIG_PIN, HIGH);
        delayMicroseconds(20); 
        digitalWrite(COMMON_TRIG_PIN, LOW);

        // Timeout 30ms (~5 เมตร) เพื่อให้ครอบคลุมระยะที่ไกลขึ้น
        duration = pulseIn(echoPin, HIGH, 30000); 
        
        if (duration > 0) break;
        delay(20); 
    }

    if (duration == 0) return -1.0;
    float distance = ((duration / 2.0) * 0.0343) + DISTANCE_OFFSET;
    
    if (distance < 20.0 || distance > 450.0) return -1.0;
    return distance;
}

void readUltrasonic(float &left, float &right) {
    // 1. อ่านซ้าย
    left = getSingleDistance(ECHO_LEFT_PIN);
    
    // 2. พักนานขึ้น (50ms) เพื่อให้เสียงเก่าจางหายไปจนหมด ป้องกันคลื่นตีกัน
    delay(50); 
    
    // 3. อ่านขวา
    right = getSingleDistance(ECHO_RIGHT_PIN);
}
