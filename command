# launch
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch mower_bot_description launch_sim.launch.py


# Teleop
ros2 run teleop_twist_keyboard teleop_twist_keyboard


# SLAM
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True


# Launch Map on Rviz2
ros2 launch nav2_bringup bringup_launch.py use_sim_time:=True map:=/home/nhio/ros2_ws/src/mower_bot_description/maps/my_map.yaml

# เปิดGazebo
cd ~/ros2_ws && source install/setup.bash
ros2 launch mower_bot_description launch_sim.launch.py

# Nav2
cd ~/ros2_ws
source install/setup.bash
ros2 launch nav2_bringup bringup_launch.py \
use_sim_time:=True \
map:=/home/nhio/ros2_ws/src/mower_bot_description/maps/my_map.yaml \
params_file:=/home/nhio/ros2_ws/src/mower_bot_description/config/my_nav2_params.yaml

# เปิด Bridge
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 run mower_bot_description serial_bridge.py

# เปิด ros2 topic list (แบบ diagram)
ros2 run rqt_graph rqt_graph



rm -rf build/ install/
colcon build --symlink-install
source install/setup.bash
ros2 launch mower_bot_description launch_sim.launch.py

# หา USB หา port
ls /dev/tty{ACM,USB}*

# check topic Ultrasonic
ros2 topic list
ros2 topic echo /ultrasonic/center

#------------ connect Teleop 2 STM -------------
source ~/ros2_ws/install/setup.bash

#manual v1 
    ros2 run robot_bridge teleop_stm #Terminal 1
    ros2 run teleop_twist_keyboard teleop_twist_keyboard #Terminal 2
    ros2 topic pub --once /engine_cmd std_msgs/msg/Int8 "{data: 1}" #Terminal 3 

    ros2 topic pub --once /throttle_cmd std_msgs/msg/Float32 "{data: 40.0}" #เร่งเครื่อง 40%
#manual v2  Terminal 1
cd ~/ros2_ws
colcon build --packages-select robot_bridge --symlink-install
source install/setup.bash
ros2 run robot_bridge teleop_stm
 # Terminal 2
cd ~/ros2_ws
colcon build --packages-select robot_bridge --symlink-install
source install/setup.bash
ros2 run robot_bridge mower_teleop_key

#Localization
 # Terminal 1
ros2 launch robot_bridge hardware_bringup.launch.py
 # Terminal 2
ros2 launch robot_bridge localization.launch.py
 # Terminal 3
rviz2 -d /home/nhio/ros2_ws/src/mower_bot_description/config/view_bot.rviz

# Nav2
cd ~/ros2_ws
colcon build --packages-select robot_bridge --symlink-install
source install/setup.bash
ros2 launch robot_bridge hardware_bringup.launch.py

cd ~/ros2_ws
colcon build --packages-select robot_bridge --symlink-install
source install/setup.bash
ros2 launch robot_bridge localization.launch.py

cd ~/ros2_ws
source install/setup.bash
ros2 launch robot_bridge navigation.launch.py

# Limit speed Nav2
desired_linear_vel: 0.2
max_velocity: [0.2, 0.0, 1.0]

#-------------- เปิด Terminal --------------
cd ~/ros2_ws && colcon build --packages-select robot_bridge --symlink-install&&source install/setup.bash
./start_robot.sh

#------------- เปิด SIM -------------------------
cd ~/ros2_ws
colcon build --packages-select robot_bridge --symlink-install
./start_sim.sh

# ดูIMUแบบสั้น ฉพาะความเร็วการหมุน (Angular Velocity)
ros2 topic echo /camera/camera/imu --field angular_velocity

#Test IMU
cd ~/ros2_ws && source install/setup.bash
ros2 launch robot_bridge imu_test.launch.py

ros2 topic echo /odometry/filtered --field pose.pose.orientation

#ดูframesทั้งหมด
ros2 run tf2_tools view_frames

python3 /home/nhio/ros2_ws/calibrate_robot.py angular 90

python3 /home/nhio/ros2_ws/calibrate_robot.py linear 1.0

python3 /home/nhio/ros2_ws/topic_monitor.py

https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}

python3 /home/nhio/ros2_ws/geofence_enforcer.py

python3 /home/nhio/ros2_ws/lawn_planner.py

killall -9 gzserver gzclient
ros2 daemon stop

#---- คำสั่ง set zero compass--------------- (ให้หันไปทางเหนือของจริงก่อนค่อยใช้คำสั่ง)
ros2 topic pub --once /imu/set_north std_msgs/msg/Empty {}

#----- Camera Realsense ---------
(เปิดกล้อง)
ros2 launch realsense2_camera rs_launch.py \
enable_color:=true \
enable_depth:=true \
rgb_camera.color_profile:=640x480x15 \
depth_module.profile:=640x480x15 \
initial_reset:=true

cd ~/ros2_ws&&colcon build --packages-select robot_bridge --symlink-install&& source install/setup.bash
ros2 run robot_bridge vision_node

ros2 run robot_bridge robot_dashboard

ros2 topic hz /camera/yolo/debug_image
ros2 topic hz /camera/camera/color/image_raw

nvidia-smi
