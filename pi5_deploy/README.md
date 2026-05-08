# =============================================================
#  README — Pi 5 Deploy Guide
#  Mower Robot: ROS2 Humble + Hailo AI HAT
# =============================================================

## ภาพรวม

โฟลเดอร์นี้มีทุกอย่างที่ต้องการสำหรับย้ายโปรเจกต์รถตัดหญ้าอัตโนมัติไปรันบน
Raspberry Pi 5 ผ่าน Docker

```
pi5_deploy/
├── Dockerfile            ← สูตรสร้าง Container (ROS2 + YOLO + Hailo)
├── docker-compose.yml    ← ตั้งค่า Hardware + Volume + Network
├── entrypoint.sh         ← สคริปต์เริ่มต้นใน Container
├── pi5_setup.sh          ← รันที่ Pi 5 ครั้งแรก (ติดตั้งทุกอย่าง)
├── pack_and_send.sh      ← รันที่ PC เพื่อส่งไฟล์ไป Pi 5
├── udev/                 ← ไฟล์สิทธิ์ Port (ถูกก๊อปปี้โดยอัตโนมัติ)
└── README.md             ← ไฟล์นี้
```

---

## ขั้นตอนทั้งหมด

### ที่เครื่อง PC (ทำก่อน)

**ขั้นที่ 1:** ส่งไฟล์ทั้งหมดไปยัง Pi 5

```bash
cd /home/nhio/ros2_ws/pi5_deploy
bash pack_and_send.sh [IP ของ Pi 5] [username]
# ตัวอย่าง:
bash pack_and_send.sh 192.168.1.50 pi
```

---

### ที่ Raspberry Pi 5 (หลังรับไฟล์แล้ว)

**ขั้นที่ 2:** SSH เข้าไปที่ Pi 5

```bash
ssh pi@[IP ของ Pi 5]
```

**ขั้นที่ 3:** รัน Setup Script (ครั้งเดียว ใช้เวลา ~20-30 นาที)

```bash
cd ~/mower_ros
bash pi5_setup.sh
```

สคริปต์นี้จะ:
- ติดตั้ง Docker อัตโนมัติ
- ติดตั้ง Hailo AI HAT Driver
- ติดตั้ง Udev Rules (ชื่อ Port ถาวร)
- Build Docker Image

**ขั้นที่ 4:** Logout แล้ว Login ใหม่ (สำคัญ!)

```bash
logout
ssh pi@[IP]
```

**ขั้นที่ 5:** รัน ROS2

```bash
cd ~/mower_ros
docker compose up
```

---

## คำสั่งที่ใช้บ่อย

### รัน/หยุด

```bash
# รันใน background
docker compose up -d

# รันแบบเห็น log
docker compose up

# หยุด
docker compose down

# ดู logs
docker compose logs -f
```

### เข้าไปใน Container

```bash
docker exec -it mower_ros bash
```

### รัน Node เฉพาะตัว

```bash
# รัน teleop
docker exec -it mower_ros ros2 run robot_bridge teleop_stm

# ดูรายการ Topics
docker exec -it mower_ros ros2 topic list

# ดูสถานะ Nav2
docker exec -it mower_ros ros2 node list
```

### ดูสถานะ Hailo

```bash
# บน Host Pi 5 (ไม่ต้องเข้า Docker)
hailortcli fw-control identify

# ตรวจสอบ Device
ls -la /dev/hailo0
```

---

## การปรับแต่ง

### เปลี่ยน Launch File ที่รันตอน Start

แก้ไขใน `docker-compose.yml` ส่วน `command:`:

```yaml
command: >
  bash -c "ros2 launch robot_bridge [ชื่อ launch file].py"
```

### ปรับแต่ง Nav2 Parameters

แก้ไขไฟล์ `config/nav2_params.yaml` ใน Host โดยตรง
(ไม่ต้อง rebuild Image เพราะ mount เป็น Volume ไว้แล้ว)
แล้ว restart Container:

```bash
docker compose restart
```

### เพิ่ม YOLO Model ใหม่

วางไฟล์ `.pt` หรือ `.hef` ไว้ใน `~/mower_ros/models/`
แล้วเปลี่ยน `model_path` ใน launch file

---

## ⚠️ สิ่งสำคัญที่ต้องรู้

### เรื่อง Hailo Version
เวอร์ชันของ `hailort` ใน Docker **ต้องตรงกับ** ที่ติดตั้งบน Pi 5 เสมอ
ถ้า Pi 5 ลง `hailo-all` version ใหม่กว่า ต้อง rebuild Image ใหม่:

```bash
# ตรวจสอบ version บน Pi 5
hailortcli --version

# Rebuild ด้วย version ที่ถูกต้อง
docker build --build-arg HAILORT_VERSION=X.X.X -t mower_ros:latest .
```

### เรื่อง YOLO บน Hailo
ไฟล์ `.pt` ของ YOLO (ultralytics format) ต้องแปลงเป็น `.hef` ก่อน
จึงจะรันบน Hailo NPU ได้:

```bash
# แปลง YOLO → Hailo HEF (รันใน Container)
docker exec -it mower_ros bash -c "
  yolo export model=yolo11n.pt format=hailo imgsz=320 half=true
"
```

ถ้ายังไม่แปลง YOLO จะรันบน CPU โดยอัตโนมัติ (ช้ากว่าแต่ยังทำงานได้)

### เรื่อง RealSense บน Pi 5
Intel RealSense อาจต้องติดตั้ง firmware บน Pi 5 ด้วย:
```bash
# บน Host Pi 5
sudo apt-get install librealsense2-utils
rs-firmware-check
```

---

## Troubleshooting

| ปัญหา | วิธีแก้ |
|---|---|
| `/dev/stm32` ไม่ปรากฏ | รัน `sudo udevadm trigger` แล้วเสียบสาย STM32 ใหม่ |
| `/dev/hailo0` ไม่ปรากฏ | `sudo modprobe hailo_pci` หรือรีสตาร์ต Pi 5 |
| YOLO ช้า (CPU mode) | แปลง model เป็น `.hef` ดูหัวข้อด้านบน |
| Nav2 ไม่ทำงาน | ตรวจสอบ `config/nav2_params.yaml` ว่า mount ถูกต้อง |
| RViz2 ไม่แสดงผล | ต่อจอโดยตรงกับ Pi 5 หรือใช้ `ssh -X` |
| Container เริ่มไม่ได้ | `docker compose logs` ดู error แล้ว report |
