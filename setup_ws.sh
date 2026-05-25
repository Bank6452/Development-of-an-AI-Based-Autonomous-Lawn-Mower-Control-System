#!/bin/bash
# =============================================================================
# setup_ws.sh — Source ROS2 workspace จากทุก directory
# =============================================================================
# วิธีใช้:
#   source ~/ros2_final_project_ws/setup_ws.sh
#
# หรือเพิ่มลงใน ~/.bashrc เพื่อ auto-source ทุกครั้ง:
#   echo "source ~/ros2_final_project_ws/setup_ws.sh" >> ~/.bashrc

# หา path ของ workspace จากตำแหน่งของสคริปต์นี้
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source ROS2 Humble
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
    echo "✅ sourced: ROS2 Humble"
else
    echo "❌ ไม่พบ ROS2 Humble ที่ /opt/ros/humble"
    return 1
fi

# Source workspace install
if [ -f "${WS_DIR}/install/setup.bash" ]; then
    source "${WS_DIR}/install/setup.bash"
    echo "✅ sourced: ${WS_DIR}/install/setup.bash"
else
    echo "⚠️  ยังไม่ได้ build — รัน: cd ${WS_DIR} && colcon build --symlink-install"
fi

# Export workspace path เป็น env variable สำหรับสคริปต์อื่น
export ROS2_WS="${WS_DIR}"
export CONFIG_DIR="${WS_DIR}/config"

echo ""
echo "📁 Workspace : ${ROS2_WS}"
echo "📁 Config    : ${CONFIG_DIR}"
echo ""
echo "🚀 พร้อมใช้งาน! ลองพิมพ์: ros2 topic list"
