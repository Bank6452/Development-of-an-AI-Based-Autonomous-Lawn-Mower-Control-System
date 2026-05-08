#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include <Arduino.h>
#include <Wire.h>
#include <INA226_WE.h>

void initPowerMonitor();
void readPowerData(float &volt, float &curr, float &power);

#endif
