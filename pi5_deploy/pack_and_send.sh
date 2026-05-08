#!/bin/bash
# =============================================================
#  pack_and_send.sh
#  รันบนเครื่อง PC นี้ — จัดแพ็คไฟล์และส่งไปยัง Pi 5
#  คำสั่ง: bash pack_and_send.sh [IP ของ Pi 5]
#  ตัวอย่าง: bash pack_and_send.sh 192.168.1.100
# =============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PI5_IP="${1:-192.168.1.100}"
PI5_USER="${2:-pi}"
PI5_TARGET_DIR="/home/${PI5_USER}/mower_ros"
WORKSPACE_DIR="/home/nhio/ros2_ws"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║     Pack & Send to Raspberry Pi 5          ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"
echo "  Target: ${PI5_USER}@${PI5_IP}:${PI5_TARGET_DIR}"
echo ""

# ── ตรวจสอบ argument ─────────────────────────────────────────
if [ "$PI5_IP" = "192.168.1.100" ]; then
    echo -e "${YELLOW}⚠️  ใส่ IP ของ Pi 5 ด้วยนะครับ:"
    echo -e "   bash pack_and_send.sh [IP_ADDRESS] [USERNAME]"
    echo -e "   ตัวอย่าง: bash pack_and_send.sh 192.168.1.50 pi${NC}"
    echo ""
    read -p "หรือใส่ IP ตรงนี้เลย: " PI5_IP
    [ -z "$PI5_IP" ] && { echo "ยกเลิก"; exit 1; }
fi

# ── ทดสอบ SSH ────────────────────────────────────────────────
echo -e "${GREEN}[1/5] ทดสอบการเชื่อมต่อ SSH...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "${PI5_USER}@${PI5_IP}" "echo OK" 2>/dev/null; then
    echo -e "${YELLOW}  ⚠️  ยังไม่มี SSH Key — กำลังตั้งค่า SSH Key...${NC}"
    ssh-keygen -t ed25519 -f ~/.ssh/id_pi5 -N "" -q 2>/dev/null || true
    ssh-copy-id -i ~/.ssh/id_pi5.pub "${PI5_USER}@${PI5_IP}" || {
        echo -e "${RED}  ❌ ไม่สามารถเชื่อมต่อ SSH ได้ ตรวจสอบ IP และ Username${NC}"
        exit 1
    }
fi
echo "  ✅ เชื่อมต่อ SSH สำเร็จ"

# ── สร้างโฟลเดอร์ที่ Pi 5 ───────────────────────────────────
echo -e "\n${GREEN}[2/5] สร้างโฟลเดอร์ที่ Pi 5...${NC}"
ssh "${PI5_USER}@${PI5_IP}" "mkdir -p ${PI5_TARGET_DIR}/udev"
echo "  ✅ สร้าง ${PI5_TARGET_DIR} แล้ว"

# ── ก๊อปปี้ไฟล์ Deploy ──────────────────────────────────────
echo -e "\n${GREEN}[3/5] ก๊อปปี้ไฟล์ Deploy...${NC}"

rsync -avz --progress \
    "${WORKSPACE_DIR}/pi5_deploy/" \
    "${PI5_USER}@${PI5_IP}:${PI5_TARGET_DIR}/"
echo "  ✅ ก๊อปปี้ pi5_deploy/ แล้ว"

# ── ก๊อปปี้ Source Code ──────────────────────────────────────
echo -e "\n${GREEN}[4/5] ก๊อปปี้ Source Code (src/)...${NC}"
echo -e "  ${YELLOW}⏳ อาจใช้เวลาสักครู่...${NC}"

rsync -avz --progress \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.zip" \
    --exclude="*.backup_today" \
    "${WORKSPACE_DIR}/src/" \
    "${PI5_USER}@${PI5_IP}:${PI5_TARGET_DIR}/src/"
echo "  ✅ ก๊อปปี้ src/ แล้ว"

# ── ก๊อปปี้ YOLO Model ───────────────────────────────────────
echo -e "\n${GREEN}[5/5] ก๊อปปี้ YOLO Model และ Udev Rules...${NC}"

# YOLO Model
if [ -f "${WORKSPACE_DIR}/yolo11n.pt" ]; then
    rsync -avz --progress \
        "${WORKSPACE_DIR}/yolo11n.pt" \
        "${PI5_USER}@${PI5_IP}:${PI5_TARGET_DIR}/"
    echo "  ✅ ก๊อปปี้ yolo11n.pt แล้ว"
fi

# Udev Rules
rsync -avz \
    /etc/udev/rules.d/98-gps.rules \
    /etc/udev/rules.d/99-stm32.rules \
    /etc/udev/rules.d/99-realsense-libusb.rules \
    "${PI5_USER}@${PI5_IP}:${PI5_TARGET_DIR}/udev/" 2>/dev/null || {
    echo -e "  ${YELLOW}⚠️  Udev rules บางไฟล์ไม่พบ — จะสร้างอัตโนมัติตอน setup${NC}"
}

# ── ให้สิทธิ์ script ─────────────────────────────────────────
ssh "${PI5_USER}@${PI5_IP}" \
    "chmod +x ${PI5_TARGET_DIR}/pi5_setup.sh ${PI5_TARGET_DIR}/entrypoint.sh"

# ── สรุป ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗"
echo -e "║  ✅ ส่งไฟล์เสร็จสมบูรณ์!                   ║"
echo -e "╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ขั้นต่อไปที่ Pi 5:"
echo ""
echo -e "  ${BLUE}# SSH เข้า Pi 5${NC}"
echo -e "  ssh ${PI5_USER}@${PI5_IP}"
echo ""
echo -e "  ${BLUE}# ไปที่โฟลเดอร์${NC}"
echo -e "  cd ${PI5_TARGET_DIR}"
echo ""
echo -e "  ${BLUE}# รัน setup (ครั้งเดียว)${NC}"
echo -e "  bash pi5_setup.sh"
echo ""
echo -e "  ${BLUE}# หลัง setup เสร็จ — รัน ROS2${NC}"
echo -e "  docker compose up"
