#!/bin/bash

# สคริปต์สำหรับรัน NTRIP Client แยกเพื่อ Warm-up RTK-GPS
# รันตัวนี้ทิ้งไว้เพื่อให้ GPS ทำระดับ Fixed ตลอดเวลา

WS_DIR=$(pwd)
source /opt/ros/humble/setup.bash
source ${WS_DIR}/install/setup.bash

echo "🚀 Starting NTRIP Client for RTK-GPS Warm-up..."

ros2 run robot_bridge ntrip_client --ros-args \
    -p ip:="!!str 192.168.1.108" \
    -p port:=2116 \
    -p mountpoint:="!!str KMUTNB65" \
    -p user:="!!str KMUTNB" \
    -p password:="!!str 65030" \
    -p serial_port:="/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0" \
    -p baudrate:=460800

# ถ้าโปรแกรมหลุด ให้รอ 5 วินาทีแล้วจบ
sleep 5
