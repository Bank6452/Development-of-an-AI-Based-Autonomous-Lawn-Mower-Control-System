#!/bin/bash
# =============================================================
#  pi5_setup.sh
#  รันบน Raspberry Pi 5 ครั้งเดียวก่อนใช้งาน
#  คำสั่ง: bash pi5_setup.sh
# =============================================================

set -e  # หยุดทันทีถ้ามี error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║     Pi 5 Mower Robot — Setup Script        ║"
echo "║     ROS2 Humble + Hailo AI HAT             ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# ── ตรวจสอบว่ารันบน Pi 5 ─────────────────────────────────────
if ! grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}⚠️  ไม่พบ Raspberry Pi 5 — แต่จะติดตั้งต่อไป${NC}"
fi

# ── Step 1: อัปเดตระบบ ───────────────────────────────────────
echo -e "\n${GREEN}[1/6] อัปเดตระบบ...${NC}"
sudo apt-get update && sudo apt-get upgrade -y

# ── Step 2: ติดตั้ง Docker ───────────────────────────────────
echo -e "\n${GREEN}[2/6] ติดตั้ง Docker...${NC}"

if command -v docker &> /dev/null; then
    echo "  ✅ Docker ติดตั้งแล้ว ($(docker --version))"
else
    echo "  📦 กำลังติดตั้ง Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    echo "  ✅ Docker ติดตั้งสำเร็จ"
fi

# เพิ่ม user เข้ากลุ่ม docker
sudo usermod -aG docker $USER
echo "  ✅ เพิ่ม $USER เข้ากลุ่ม docker แล้ว"

# ── Step 3: ติดตั้ง Docker Compose ──────────────────────────
echo -e "\n${GREEN}[3/6] ติดตั้ง Docker Compose...${NC}"

if command -v docker compose &> /dev/null; then
    echo "  ✅ Docker Compose พร้อมแล้ว"
else
    sudo apt-get install -y docker-compose-plugin
    echo "  ✅ Docker Compose ติดตั้งสำเร็จ"
fi

# ── Step 4: ติดตั้ง Hailo AI HAT Driver ─────────────────────
echo -e "\n${GREEN}[4/6] ติดตั้ง Hailo AI HAT Driver...${NC}"

if [ -e /dev/hailo0 ]; then
    echo "  ✅ Hailo พร้อมแล้ว (/dev/hailo0 พบแล้ว)"
else
    echo "  📦 กำลังเพิ่ม Hailo Repository..."

    # เพิ่ม Raspberry Pi repository (ต้องมี hailo-all อยู่ใน rpi-repo)
    sudo apt-get install -y rpi-update 2>/dev/null || true

    # ติดตั้ง hailo-all จาก Raspberry Pi's apt repository
    # (ต้องใช้ Raspberry Pi OS Bookworm เท่านั้น)
    sudo apt-get install -y hailo-all 2>/dev/null || {
        echo -e "  ${YELLOW}⚠️  hailo-all ไม่พบใน apt repository"
        echo -e "  ดาวน์โหลดด้วยตนเองที่: https://github.com/hailo-ai/hailort/releases"
        echo -e "  แล้วรัน: sudo dpkg -i hailort_*.deb${NC}"
    }

    # โหลด kernel module
    sudo modprobe hailo_pci 2>/dev/null || true

    if [ -e /dev/hailo0 ]; then
        echo "  ✅ Hailo AI HAT พร้อมแล้ว!"

        # ตรวจสอบ version สำคัญมากสำหรับการตั้ง Docker
        echo ""
        echo -e "  ${YELLOW}⚡ เวอร์ชัน HailoRT ที่ติดตั้ง:${NC}"
        hailortcli fw-control identify 2>/dev/null | grep -i "firmware\|hailo" || true
    else
        echo -e "  ${RED}❌ ยังไม่พบ /dev/hailo0 — ลองรีสตาร์ตแล้วรันสคริปต์ใหม่${NC}"
    fi
fi

# ── Step 5: ติดตั้ง Udev Rules ───────────────────────────────
echo -e "\n${GREEN}[5/6] ติดตั้ง Udev Rules (ชื่อ Port)...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# GPS RTK Rule (FTDI FT232)
if [ -f "$SCRIPT_DIR/udev/98-gps.rules" ]; then
    sudo cp "$SCRIPT_DIR/udev/98-gps.rules" /etc/udev/rules.d/
    echo "  ✅ 98-gps.rules → /dev/gps_rtk"
else
    echo "  📝 สร้าง 98-gps.rules..."
    sudo bash -c 'echo "SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6001\", SYMLINK+=\"gps_rtk\"" > /etc/udev/rules.d/98-gps.rules'
    echo "  ✅ 98-gps.rules สร้างแล้ว → /dev/gps_rtk"
fi

# STM32 Rule (CH340)
if [ -f "$SCRIPT_DIR/udev/99-stm32.rules" ]; then
    sudo cp "$SCRIPT_DIR/udev/99-stm32.rules" /etc/udev/rules.d/
    echo "  ✅ 99-stm32.rules → /dev/stm32"
else
    echo "  📝 สร้าง 99-stm32.rules..."
    sudo bash -c 'echo "SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"1a86\", ATTRS{idProduct}==\"7523\", SYMLINK+=\"stm32\", MODE=\"0666\"" > /etc/udev/rules.d/99-stm32.rules'
    echo "  ✅ 99-stm32.rules สร้างแล้ว → /dev/stm32"
fi

# RealSense Rule
if [ -f "$SCRIPT_DIR/udev/99-realsense-libusb.rules" ]; then
    sudo cp "$SCRIPT_DIR/udev/99-realsense-libusb.rules" /etc/udev/rules.d/
    echo "  ✅ 99-realsense-libusb.rules ติดตั้งแล้ว"
fi

# โหลด udev rules ใหม่
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "  ✅ Udev rules โหลดแล้ว"

# เพิ่ม user เข้ากลุ่ม dialout และ plugdev
sudo usermod -aG dialout,plugdev $USER
echo "  ✅ เพิ่มสิทธิ์ Serial Port ให้ $USER แล้ว"

# ── Step 6: Build Docker Image ────────────────────────────────
echo -e "\n${GREEN}[6/6] Build Docker Image...${NC}"
echo -e "  ${YELLOW}⏳ อาจใช้เวลา 15-30 นาที ในการดาวน์โหลดและ Build ครั้งแรก${NC}"
echo ""

# ตรวจสอบ hailort version สำหรับใส่ใน Docker build
HAILO_VER=$(hailortcli --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)
if [ -n "$HAILO_VER" ]; then
    echo "  🔖 ใช้ HailoRT version: $HAILO_VER"
    BUILD_ARG="--build-arg HAILORT_VERSION=$HAILO_VER"
else
    echo "  🔖 ใช้ HailoRT version เริ่มต้น: 4.18.0"
    BUILD_ARG="--build-arg HAILORT_VERSION=4.18.0"
fi

cd "$SCRIPT_DIR"
docker build $BUILD_ARG -t mower_ros:latest . && {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗"
    echo -e "║  ✅ Setup เสร็จสมบูรณ์!                    ║"
    echo -e "╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${YELLOW}⚠️  สำคัญ: Logout แล้ว Login ใหม่ก่อนรันครั้งแรก"
    echo -e "     เพื่อให้สิทธิ์ docker และ dialout มีผล${NC}"
    echo ""
    echo -e "  วิธีรัน ROS2:"
    echo -e "    ${BLUE}docker compose up${NC}              — รัน background"
    echo -e "    ${BLUE}docker compose up --attach${NC}     — รูกับ terminal"
    echo -e "    ${BLUE}docker compose down${NC}            — หยุด"
    echo ""
    echo -e "  เข้าไปใน Container:"
    echo -e "    ${BLUE}docker exec -it mower_ros bash${NC}"
} || {
    echo -e "${RED}❌ Build ล้มเหลว — ดู error ด้านบน${NC}"
    exit 1
}
