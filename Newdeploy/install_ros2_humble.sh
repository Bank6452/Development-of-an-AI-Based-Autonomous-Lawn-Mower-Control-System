#!/bin/bash
set -e

# กำหนดให้ติดตั้งแบบ Non-interactive (ไม่ถามคำถาม) และตั้ง Timezone เป็น Asia/Bangkok
export DEBIAN_FRONTEND=noninteractive
sudo ln -fs /usr/share/zoneinfo/Asia/Bangkok /etc/localtime

echo "🚀 Starting ROS 2 Humble Base Installation..."

# 1. Setup Locale
echo "--- Setting up Locale ---"
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 2. Setup Sources
echo "--- Setting up Sources ---"
sudo apt install software-properties-common -y
sudo add-apt-repository universe -y

sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3. Install ROS 2 packages
echo "--- Installing ROS 2 Humble Desktop ---"
sudo apt update
sudo apt install ros-humble-desktop -y

echo "--- Installing Dev Tools (colcon, etc.) ---"
sudo apt install ros-dev-tools -y
sudo apt install python3-colcon-common-extensions python3-venv -y

# 3.5 Grant execute permissions to all workspace scripts
echo "--- Granting execute permissions to shell scripts ---"
chmod +x *.sh 2>/dev/null || true
if [ -d "src/rplidar_ros/scripts" ]; then
    chmod +x src/rplidar_ros/scripts/*.sh 2>/dev/null || true
fi

# 4. Clean system packages cache
echo "--- Cleaning system packages cache ---"
sudo apt-get clean

echo "✅ ROS 2 Humble Installation Complete!"
echo "Now you can run the dependency script again."
