#!/bin/bash
# =============================================================
#  entrypoint.sh
#  Docker Entrypoint — source ROS2 environment ก่อนรันทุกครั้ง
# =============================================================

set -e

# Source ROS2 environments
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash 2>/dev/null || true

# แสดงสถานะ Hailo (ถ้ามีอุปกรณ์ต่ออยู่)
if [ -e /dev/hailo0 ]; then
    echo "✅ Hailo AI HAT พร้อมใช้งาน (/dev/hailo0 พบแล้ว)"
else
    echo "⚠️  ไม่พบ /dev/hailo0 — YOLO จะรันบน CPU แทน"
fi

echo "🚀 ROS2 Humble Ready | Domain ID: ${ROS_DOMAIN_ID:-0}"
echo "   Workspace: /ros2_ws"
echo ""

exec "$@"
