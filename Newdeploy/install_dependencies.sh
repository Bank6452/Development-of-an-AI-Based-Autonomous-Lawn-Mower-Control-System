#!/bin/bash

# =================================================================
# Autonomous Mower - Full Dependency Installer
# =================================================================

echo "🚀 Starting Full Dependency Installation..."

# Detect and configure ROS 2 colcon ignore for virtual environments
if [ -n "$VIRTUAL_ENV" ]; then
    echo "⚙️ Active Virtual Environment detected: $VIRTUAL_ENV"
    touch "$VIRTUAL_ENV/COLCON_IGNORE"
    echo "   ✅ Created COLCON_IGNORE to prevent build tool interference."
elif [ -d "venv" ]; then
    echo "⚙️ Local venv directory detected."
    touch venv/COLCON_IGNORE
    echo "   ✅ Created COLCON_IGNORE inside venv/."
fi

# 1. Update System
echo "--- Updating System Packages ---"
sudo apt update && sudo apt upgrade -y

# 2. Install ROS 2 Dependencies (Humble)
echo "--- Installing ROS 2 System Dependencies ---"
sudo apt install -y \
    ros-humble-robot-localization \
    ros-humble-nmea-msgs \
    ros-humble-cv-bridge \
    ros-humble-realsense2-camera \
    ros-humble-nav2-msgs \
    ros-humble-nav2-bringup \
    ros-humble-xacro \
    ros-humble-diagnostic-msgs \
    ros-humble-diagnostic-updater \
    python3-pip \
    python3-colcon-common-extensions

# 2.1 Install RealSense Utils (Optional - installed separately to prevent blocking the main install)
echo "--- Installing RealSense Utilities (Optional) ---"
sudo apt install -y librealsense2-utils 2>/dev/null || echo "⚠️ Warning: librealsense2-utils not found in default repository, skipping optional tool."

# 3. Install Python Libraries via pip
echo "--- Installing Python Libraries ---"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "❌ requirements.txt not found! Installing core libs manually..."
    pip3 install "numpy==1.23.5" opencv-python pyserial shapely ultralytics PyYAML torch torchvision torchaudio
fi

# 4. Install Udev Rules (For STM32 and GPS)
echo "--- Installing Udev Rules ---"
if [ -f "99-stm32.rules" ]; then
    sudo cp 99-stm32.rules /etc/udev/rules.d/
    echo "✅ 99-stm32.rules installed."
fi

if [ -f "98-gps.rules" ]; then
    sudo cp 98-gps.rules /etc/udev/rules.d/
    echo "✅ 98-gps.rules installed."
fi

echo "--- Reloading Udev Rules ---"
sudo udevadm control --reload-rules && sudo udevadm trigger

# 4.1 Configure Serial Port Group Permissions (dialout)
echo "--- Configuring Serial Port Access (dialout group) ---"
if [ "$USER" != "root" ] && [ -n "$USER" ]; then
    echo "Adding user $USER to dialout group..."
    sudo usermod -aG dialout "$USER"
    echo "✅ User $USER added to dialout group. (You might need to log out and log back in for this to take effect)."
else
    echo "Running as root or user not set, skipping dialout group addition."
fi

# 5. Optional: Hailo-8L SDK (For Raspberry Pi 5 AI)
echo "--- Checking for Hailo SDK (Optional) ---"
echo "NOTE: If you are using Raspberry Pi 5 with Hailo-8L AI kit,"
echo "you should run: sudo apt install hailo-all"

# 5.1 Grant execute permissions to all workspace scripts
echo "--- Granting execute permissions to shell scripts ---"
chmod +x *.sh 2>/dev/null || true
if [ -d "src/rplidar_ros/scripts" ]; then
    chmod +x src/rplidar_ros/scripts/*.sh 2>/dev/null || true
fi

# 6. Cleanup (Recommended for Docker containers to save space)
echo "--- Cleaning system packages cache ---"
sudo apt-get clean

if [ -f /.dockerenv ]; then
    echo "Docker detected. Purging pip cache to reclaim disk space..."
    pip3 cache purge 2>/dev/null || true
    rm -rf ~/.cache/pip
fi

echo "✅ ALL-IN-ONE Installation Complete!"
echo "🚀 Next Steps:"
echo "   1. source /opt/ros/humble/setup.bash"
echo "   2. colcon build --symlink-install"
echo "   3. source install/setup.bash"
