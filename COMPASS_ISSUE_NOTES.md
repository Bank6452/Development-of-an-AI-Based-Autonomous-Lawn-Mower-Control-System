# 🧭 Compass & Localization Crash Issue

## 🚨 Problem Description
After integrating the GY-273 (QMC5883L) compass, the `robot_localization` (EKF) and Navigation (Nav2) stacks crash or report missing transforms. This is likely caused by `NaN` values from the compass during initialization or interference.

## 🛠️ Roadmap for Dual-Antenna RTK Upgrade
If switching to a Dual-Antenna RTK (Heading) system, follow these steps to integrate and tune:

### 1. Hardware & Driver Setup
- **Ports**: Connect via USB. Check if the port is `/dev/gps_rtk` or a new one like `/dev/gps_heading`.
- **Driver**: The `ntrip_client.py` will read the NMEA sentences (usually `$GNHDT`) from the new board.
- **STM32**: REMOVE any magnetic compass (`GY-273`) logic from STM32 to avoid protocol conflicts.

### 2. ROS 2 Software Synchronization
- Update `teleop_stm.py` to Subscribe to the new GPS Heading topic instead of parsing `H,` from STM32.
- Recommended Topic: `/compass/heading` (Float64) or `/gps/heading`.

### 3. EKF Tuning (`ekf.yaml`)
This is the most critical part for stability:
- **Yaw Covariance**: Set to a very small value (e.g., `0.01` or `0.001`) to tell ROS to trust the RTK's absolute heading more than the wheel encoders.
- **Yaw Offset**: Measure the physical mounting angle of the two antennas. If they are not perfectly parallel to the robot's centerline, compensate it using the `yaw_offset` parameter.
- **Outlier Rejection**: Tune `yaw_rejection_threshold` to prevent the EKF from "locking out" the good GPS data if the IMU drifts too far during signal loss.

---

## 🕵️‍♂️ Root Cause Analysis (Old Magnetic Compass)
- The EKF node relies on valid numerical data.
- If STM32 sends `H,nan`, it infects the `odom_th` and subsequent `x/y` calculations.
- **Solution**: Always check `if math.isnan(heading): return` in the ROS driver.

## ✨ Benefits of Dual-Antenna RTK
- **Absolute Accuracy**: No "Hard Iron" (metallic) interference.
- **No Calibration**: Unlike magnetometers, dual-antennas don't need to be rotated 360 degrees to "learn" the environment.
- **Centimeter-Level Heading**: Essential for straight lines in autonomous mowing.
