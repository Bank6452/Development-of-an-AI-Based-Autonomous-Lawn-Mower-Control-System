#include "power_monitor.h"

#define I2C_ADDRESS_INA226 0x40
INA226_WE ina226 = INA226_WE(I2C_ADDRESS_INA226);

void initPowerMonitor() {
    if(!ina226.init()){
        Serial.println("❌ ERROR: INA226 not detected!");
    } else {
        ina226.setResistorRange(0.0015, 50.0);
        ina226.waitUntilConversionCompleted();
        Serial.println("✅ Power Monitor Ready!");
    }
}

void readPowerData(float &volt, float &curr, float &power) {
    float sumVolt = 0;
    float sumCurr = 0;
    int samples = 10;

    for(int i = 0; i < samples; i++) {
        sumVolt += ina226.getBusVoltage_V();
        sumCurr += ina226.getCurrent_mA();
        delay(10); 
    }

    float avgVolt = sumVolt / samples;
    float avgCurr = sumCurr / samples;

    // 🎯 ใช้ Factor ที่เราจูนกันไว้
    volt = avgVolt * 1.04; 
    curr = (avgCurr / 1000.0) * 0.915;
    power = volt * abs(curr);
}
