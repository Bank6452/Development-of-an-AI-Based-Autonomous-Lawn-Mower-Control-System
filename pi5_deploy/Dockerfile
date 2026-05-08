# =============================================================
#  Dockerfile — ROS2 Humble + Mower Robot + Hailo AI HAT
#  Target: Raspberry Pi 5 (ARM64) with AI HAT+
#  Base OS on Pi: Raspberry Pi OS Bookworm 64-bit
# =============================================================

FROM ros:humble-ros-base-jammy

# ── ตัวแปรที่ปรับได้ ──────────────────────────────────────────
# เวอร์ชันของ hailort ต้องตรงกับที่ติดตั้งบน Pi 5
# ดูเวอร์ชันที่ Pi 5 ด้วย: hailortcli fw-control identify
ARG HAILORT_VERSION=4.18.0

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV ROS_DOMAIN_ID=0
ENV RCUTILS_COLORIZED_OUTPUT=1

# ── 1. ติดตั้ง ROS2 Packages ─────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Navigation Stack
    ros-humble-nav2-bringup \
    ros-humble-navigation2 \
    ros-humble-nav2-msgs \
    ros-humble-nav2-simple-commander \
    # Localization
    ros-humble-robot-localization \
    ros-humble-slam-toolbox \
    ros-humble-cartographer \
    ros-humble-cartographer-ros \
    # Hardware Drivers
    ros-humble-rplidar-ros \
    ros-humble-realsense2-camera \
    ros-humble-realsense2-description \
    # Vision
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    ros-humble-vision-msgs \
    # GPS / NMEA
    ros-humble-nmea-msgs \
    ros-humble-nmea-navsat-driver \
    ros-humble-ntrip-client \
    ros-humble-rtcm-msgs \
    ros-humble-gps-msgs \
    # TF & Robot Description
    ros-humble-tf2 \
    ros-humble-tf2-ros \
    ros-humble-tf2-tools \
    ros-humble-tf2-geometry-msgs \
    ros-humble-tf-transformations \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    # Messages
    ros-humble-sensor-msgs \
    ros-humble-geometry-msgs \
    ros-humble-nav-msgs \
    ros-humble-std-msgs \
    ros-humble-std-srvs \
    ros-humble-diagnostic-msgs \
    ros-humble-diagnostic-updater \
    ros-humble-action-msgs \
    # Tools
    ros-humble-teleop-twist-keyboard \
    ros-humble-rqt \
    ros-humble-rqt-common-plugins \
    ros-humble-rviz2 \
    # Build tools
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-setuptools \
    # System utils
    git \
    wget \
    curl \
    vim \
    usbutils \
    udev \
    && rm -rf /var/lib/apt/lists/*

# ── 2. ติดตั้ง Python Libraries ──────────────────────────────
RUN pip3 install --no-cache-dir \
    # Serial Communication
    pyserial \
    # Math & Science
    numpy \
    scipy \
    shapely \
    matplotlib \
    # Transforms
    transforms3d \
    # AI / Vision
    ultralytics \
    opencv-python-headless \
    # Hailo Python Bindings (ต้องตรงกับ Host)
    hailort==${HAILORT_VERSION} \
    # Utilities
    pyyaml \
    requests

# ── 3. ติดตั้ง Hailo TAPPAS Python API (สำหรับรัน YOLO บน NPU) ──
# ใช้สำหรับโหลดไฟล์ .hef และส่งรูปเข้า Hailo chip โดยตรง
# (ถ้า hailo-tappas ไม่มีใน pip ให้คอมเมนต์บรรทัดนี้ออก)
# RUN pip3 install hailo-tappas-core --no-cache-dir

# ── 4. Setup Workspace ────────────────────────────────────────
WORKDIR /ros2_ws

# ก๊อปปี้ source code ทั้งหมด
COPY src/ ./src/

# ก๊อปปี้ YOLO model
COPY yolo11n.pt /ros2_ws/yolo11n.pt

# ── 5. Build ROS2 Workspace ───────────────────────────────────
RUN . /opt/ros/humble/setup.sh && \
    rosdep update --rosdistro=humble && \
    rosdep install --from-paths src --ignore-src -r -y --rosdistro=humble && \
    colcon build --symlink-install \
        --cmake-args -DCMAKE_BUILD_TYPE=Release \
    && rm -rf build/ log/

# ── 6. Setup Environment ──────────────────────────────────────
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> /root/.bashrc && \
    echo "export ROS_DOMAIN_ID=0" >> /root/.bashrc

# ── 7. Entrypoint ─────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
