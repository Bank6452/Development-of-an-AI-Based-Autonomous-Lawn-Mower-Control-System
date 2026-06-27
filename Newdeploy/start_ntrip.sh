#!/bin/bash

# สคริปต์สำหรับรัน NTRIP Client แยกเพื่อ Warm-up RTK-GPS
# รันตัวนี้ทิ้งไว้เพื่อให้ GPS ทำระดับ Fixed ตลอดเวลา

WS_DIR=$(pwd)
source /opt/ros/humble/setup.bash

# Check if a virtual environment is already active, or scan for one in the workspace
if [ -n "$VIRTUAL_ENV" ]; then
    VENV_DIR="$VIRTUAL_ENV"
    echo "✓ Active Virtual Environment detected: $VENV_DIR"
else
    # Scan for any folder containing bin/activate (up to 3 levels deep)
    ACTIVATE_FILE=$(find "${WS_DIR}" -maxdepth 3 -name "activate" -path "*/bin/activate" 2>/dev/null | head -n 1)
    if [ -n "$ACTIVATE_FILE" ]; then
        VENV_DIR=$(dirname "$(dirname "$ACTIVATE_FILE")")
        echo "✓ Found Virtual Environment: $VENV_DIR"
        source "${VENV_DIR}/bin/activate"
    else
        echo "⚠️ No Virtual Environment found. Using global system packages."
    fi
fi

source ${WS_DIR}/install/setup.bash

echo "🚀 Starting NTRIP Client for RTK-GPS Warm-up..."

ros2 run robot_bridge ntrip_client --ros-args \
    --params-file ${WS_DIR}/src/robot_bridge/config/ntrip_params.yaml

# ถ้าโปรแกรมหลุด ให้รอ 5 วินาทีแล้วจบ
sleep 5
