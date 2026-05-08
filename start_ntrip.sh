#!/bin/bash

# สคริปต์สำหรับรัน NTRIP Client แยกเพื่อ Warm-up RTK-GPS
# รันตัวนี้ทิ้งไว้เพื่อให้ GPS ทำระดับ Fixed ตลอดเวลา

source /opt/ros/humble/setup.bash
source /home/nhio/ros2_ws/install/setup.bash

echo "🚀 Starting NTRIP Client for RTK-GPS Warm-up..."

ros2 run robot_bridge ntrip_client \
    --ros-args \
    --params-file /home/nhio/ros2_ws/src/robot_bridge/config/ntrip_params.yaml

# ถ้าโปรแกรมหลุด ให้รอ 5 วินาทีแล้วจบ
sleep 5
