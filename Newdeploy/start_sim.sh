#!/bin/bash

# --- Robot Simulation Startup Script ---
source /opt/ros/humble/setup.bash

# 1. Check if a virtual environment is already active, or scan for one in the workspace
if [ -n "$VIRTUAL_ENV" ]; then
    VENV_DIR="$VIRTUAL_ENV"
    echo "✓ Active Virtual Environment detected: $VENV_DIR"
else
    # Scan for any folder containing bin/activate (up to 3 levels deep)
    ACTIVATE_FILE=$(find "$(pwd)" -maxdepth 3 -name "activate" -path "*/bin/activate" 2>/dev/null | head -n 1)
    if [ -n "$ACTIVATE_FILE" ]; then
        VENV_DIR=$(dirname "$(dirname "$ACTIVATE_FILE")")
        echo "✓ Found Virtual Environment: $VENV_DIR"
        source "${VENV_DIR}/bin/activate"
    else
        echo "⚠️ No Virtual Environment found. Using global system packages."
        VENV_DIR=""
    fi
fi

if [ ! -d "src/robot_bridge" ]; then
    echo "Error: กรุณารันสคริปต์นี้จากโฟลเดอร์ ~/ros2_ws เท่านั้น"
    exit 1
fi

echo "🛑 Stopping existing ROS2 nodes..."
killall -9 gzserver gzclient
killall -9 teleop_stm arduino_reader nmea_serial_driver 2>/dev/null
pkill -9 -f "realsense2_camera" 2>/dev/null
pkill -9 -f "rs_launch" 2>/dev/null
pkill -9 -f "robot_localization" 2>/dev/null
pkill -9 -f "nav2" 2>/dev/null
pkill -9 -f "rviz2" 2>/dev/null
pkill -9 -f "gzserver" 2>/dev/null
pkill -9 -f "gzclient" 2>/dev/null
pkill -9 -f "lawn_planner" 2>/dev/null

ros2 daemon stop
ros2 daemon start

sleep 2

echo "🔨 Building Workspace..."
colcon build --symlink-install

WS_DIR=$(pwd)
SOURCE_CMD="source /opt/ros/humble/setup.bash"
if [ -n "$VENV_DIR" ]; then
    SOURCE_CMD="${SOURCE_CMD} && source ${VENV_DIR}/bin/activate"
fi
SOURCE_CMD="${SOURCE_CMD} && source ${WS_DIR}/install/setup.bash"

echo "🚀 Launching Gazebo Simulation & Systems..."

gnome-terminal --tab --title="1. GAZEBO_SIM" -- bash -c "$SOURCE_CMD && ros2 launch robot_bridge simulation.launch.py; exec bash" 
sleep 8
gnome-terminal --tab --title="2. SAFETY & PLANNER" -- bash -c "sleep 5 && $SOURCE_CMD && ros2 run robot_bridge geofence_and_planner --ros-args -p geofence_file:=${WS_DIR}/lawn_geofence_sim.yaml; exec bash"
sleep 10
gnome-terminal --tab --title="3. MOWING_EXECUTOR" -- bash -c "sleep 10 && $SOURCE_CMD && echo '🚜 รอรับพิกัดสนาม... เมื่อทุกอย่างพร้อมพิมพ์ go แล้วกด Enter' && ros2 run robot_bridge mow_zigzag; exec bash"

echo ""
echo "✅ เริ่มระบบจำลองสำเร็จ! (รอสักครู่โปรแกรมในแต่ละแท็บจะโหลดขึ้นมาตามลำดับ)"
echo "   📌 แท็บ 1 (GAZEBO)   → โลกเสมือนและระบบนำทาง (รอให้โหลด 2D Map เสร็จก่อน)"
echo "   📌 แท็บ 2 (SAFETY)   → ระบบป้องกันและคำนวณเส้นทาง (รวมร่าง Geofence + Planner)"
echo "   📌 แท็บ 3 (MOWING)   → สำหรับสั่งพิมพ์ 'go' เพื่อสั่งวิ่งเดินหน้าตามแผน!"
echo ""
