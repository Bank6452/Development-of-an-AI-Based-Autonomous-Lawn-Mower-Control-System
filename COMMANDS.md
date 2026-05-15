# 📋 Command Cheatsheet — Mower Bot ROS2 Workspace

> ⚠️ **รันสคริปต์ทุกตัวจาก workspace root เสมอ**
> ```bash
> cd ~/ros2_final_project_ws   # หรือชื่อ folder จริงบนเครื่อง
> ```

---

## 🚀 เริ่มระบบหลัก

```bash
# [หุ่นยนต์จริง] — build + เปิดทุก tab อัตโนมัติ
cd ~/ros2_final_project_ws && colcon build --packages-select robot_bridge --symlink-install && source install/setup.bash
./start_robot.sh

# [Simulation] — build + เปิด Gazebo อัตโนมัติ
cd ~/ros2_final_project_ws
colcon build --packages-select robot_bridge --symlink-install
./start_sim.sh
```

---

## 🔨 Build & Source

```bash
cd ~/ros2_final_project_ws

# Build ทั้งหมด
colcon build --symlink-install

# Build เฉพาะ package
colcon build --packages-select robot_bridge --symlink-install
colcon build --packages-select mower_bot_description --symlink-install

# Source workspace (ทำทุกครั้งหลัง build)
source /opt/ros/humble/setup.bash
source install/setup.bash
```

---

## 🤖 Launch Files

```bash
cd ~/ros2_final_project_ws && source install/setup.bash

# Terminal 1 — Hardware
ros2 launch robot_bridge hardware_bringup.launch.py

# Terminal 2 — Localization (EKF)
ros2 launch robot_bridge localization.launch.py

# Terminal 3 — Navigation (Nav2)
ros2 launch robot_bridge navigation.launch.py

# Simulation (Gazebo)
ros2 launch robot_bridge simulation.launch.py
ros2 launch mower_bot_description launch_sim.launch.py

# Test IMU
ros2 launch robot_bridge imu_test.launch.py
```

---

## 🗺️ Nav2 + SLAM + Map

```bash
# SLAM
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True

# Nav2 bringup (Simulation)
ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=True \
  map:=~/ros2_final_project_ws/src/mower_bot_description/maps/my_map.yaml \
  params_file:=~/ros2_final_project_ws/src/mower_bot_description/config/my_nav2_params.yaml

# RViz2
rviz2 -d ~/ros2_final_project_ws/src/mower_bot_description/config/view_bot.rviz
ros2 launch nav2_bringup bringup_launch.py use_sim_time:=True \
  map:=~/ros2_final_project_ws/src/mower_bot_description/maps/my_map.yaml

# ดู TF frames
ros2 run tf2_tools view_frames
```

---

## 🌿 Geofence & Planner

```bash
cd ~/ros2_final_project_ws && source install/setup.bash

# Geofence Enforcer (หุ่นยนต์จริง)
ros2 run robot_bridge geofence_enforcer \
  --ros-args -p geofence_file:=$(pwd)/config/lawn_geofence.yaml

# Geofence Enforcer (Simulation)
ros2 run robot_bridge geofence_enforcer \
  --ros-args -p geofence_file:=$(pwd)/config/lawn_geofence_sim.yaml

# Lawn Planner
ros2 run robot_bridge lawn_planner \
  --ros-args -p geofence_file:=$(pwd)/config/lawn_geofence.yaml

# Geofence + Planner รวม
ros2 run robot_bridge geofence_and_planner \
  --ros-args -p geofence_file:=$(pwd)/config/lawn_geofence.yaml

# Mowing Executor
ros2 run robot_bridge mow_zigzag
```

---

## 📡 GPS / NTRIP

```bash
./start_ntrip.sh

# หรือรันตรง
cd ~/ros2_final_project_ws && source install/setup.bash
ros2 run robot_bridge ntrip_client --ros-args \
  -p ip:="192.168.1.108" \
  -p port:=2116 \
  -p mountpoint:="KMUTNB65"
```

---

## 📷 Camera & Vision

```bash
cd ~/ros2_final_project_ws && source install/setup.bash

# เปิดกล้อง RealSense
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true enable_depth:=true \
  rgb_camera.color_profile:=640x480x15 \
  depth_module.profile:=640x480x15 \
  initial_reset:=true

# Vision Node (YOLO)
ros2 run robot_bridge vision_node

# ตรวจสอบ FPS กล้อง
ros2 topic hz /camera/yolo/debug_image
ros2 topic hz /camera/camera/color/image_raw

# GPU
nvidia-smi
```

---

## 🕹️ Teleop & Dashboard

```bash
cd ~/ros2_final_project_ws && source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard
ros2 run robot_bridge robot_dashboard
ros2 run robot_bridge straight_line_test

# ส่ง cmd_vel โดยตรง
ros2 topic pub --once /cmd_vel_teleop geometry_msgs/msg/Twist \
  "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

---

## 🧭 IMU / Compass

```bash
# Set zero compass (หันไปทางเหนือก่อน)
ros2 topic pub --once /imu/set_north std_msgs/msg/Empty {}

# Monitor IMU
ros2 topic echo /camera/camera/imu --field angular_velocity
ros2 topic echo /odometry/filtered --field pose.pose.orientation
```

---

## 🔧 Calibration

```bash
cd ~/ros2_final_project_ws && source install/setup.bash

# Calibrate (linear/angular) — ต้องรัน hardware_bringup ก่อน
python3 scripts/calibrate_robot.py linear 1.0
python3 scripts/calibrate_robot.py angular 90

python3 scripts/calibrate_linear.py

# Monitor topics
python3 scripts/topic_monitor.py
python3 scripts/monitor_imu_robot.py
```

---

## 🔌 USB / Serial Ports

```bash
ls /dev/tty{ACM,USB}*
ls /dev/serial/by-id/

# ติดตั้ง udev rules (ทำครั้งเดียว)
sudo cp config/udev/98-gps.rules   /etc/udev/rules.d/
sudo cp config/udev/99-stm32.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## 📊 Topics & Diagnostics

```bash
ros2 topic list
ros2 topic echo /ultrasonic/center
ros2 run rqt_graph rqt_graph

# Diagnostic check (บันทึก log 20 วิ)
./diagnostic_check.sh
```

---

## ⚙️ Misc

```bash
# Stop ทุก node + daemon
killall -9 gzserver gzclient 2>/dev/null
ros2 daemon stop && ros2 daemon start

# Snapshot environment
./snapshot_env.sh
```

---

## 🗺️ Map Tile URL (Google Satellite)
```
https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}
```
