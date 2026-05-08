import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Path to RealSense Launch
    realsense_launch_dir = get_package_share_directory('realsense2_camera')
    
    # 1. AI Vision Node (สมอง AI สำหรับตรวจจับสิ่งกีดขวาง)
    vision_node = Node(
        package='robot_bridge',
        executable='vision_node',
        name='vision_node',
        output='screen',
        parameters=[{
            'model_path': 'yolo11n.pt',
            'stop_distance': 2.0
        }]
    )

    # 2. STM32 Teleop (ตัวกลางส่งคำสั่งไปบอร์ดขับมอเตอร์)
    teleop_stm_node = Node(
        package='robot_bridge',
        executable='teleop_stm',
        name='teleop_stm',
        output='screen',
        parameters=[{
            'port': '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0',
            'baudrate': 115200,
            'max_speed_ms': 1.25
        }]
    )

    # 3. RealSense Camera (D435i - ปรับจูนเพื่อ AI และความเสถียร)
    realsense_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(realsense_launch_dir, 'launch', 'rs_launch.py')),
        launch_arguments={
            'enable_gyro': 'true',
            'enable_accel': 'true',
            'unite_imu_method': '2',
            'enable_sync': 'true',
            'initial_reset': 'true',
            'enable_color': 'true',
            'enable_depth': 'true',          # ✅ เปิด Depth เพื่อให้ AI วัดระยะได้
            'rgb_camera.color_profile': '640x480x15', # ✅ บังคับ 15 FPS เพื่อลดความร้อน
            'depth_module.profile': '640x480x15',     # ✅ บังคับ 15 FPS ให้เท่ากับภาพสี
            'pointcloud.enable': 'false',
        }.items()
    )

    # 4. NTRIP Client (สำหรับ RTK-GPS)
    ntrip_client_node = Node(
        package='robot_bridge',
        executable='ntrip_client',
        name='ntrip_client',
        output='screen',
        parameters=[{
            'ip': '192.168.1.108',
            'port': 2116,
            'mountpoint': 'KMUTNB65',
            'user': 'KMUTNB',
            'password': '65030',
            'serial_port': '/dev/serial/by-id/usb-FTDI_USB__-__Serial-if00-port0',
            'baudrate': 460800 
        }]
    )

    # 5. NMEA Topic Driver (ประมวลผลค่า GPS)
    nmea_gps_node = Node(
        package='nmea_navsat_driver',
        executable='nmea_topic_driver',
        name='nmea_topic_driver',
        output='screen'
    )

    # 6. Ultrasonic to LaserScan Converter
    ultrasonic_converter_node = Node(
        package='robot_bridge',
        executable='ultrasonic_converter',
        name='ultrasonic_converter',
        output='screen'
    )

    # 7. RPLiDAR A1 (ตรวจจับสิ่งกีดขวางรอบตัว)
    rplidar_node = Node(
        package='rplidar_ros',
        executable='rplidar_node',
        name='rplidar_node',
        output='screen',
        parameters=[{
            'serial_port': '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
            'serial_baudrate': 115200,
            'frame_id': 'laser_frame',
            'inverted': False,
            'angle_compensate': True,
        }]
    )

    # 8. Auto Datum Node (อ่าน Datum จาก geofence YAML → ตั้งให้ navsat_transform อัตโนมัติ)
    auto_datum_node = Node(
        package='robot_bridge',
        executable='auto_datum_node',
        name='auto_datum_node',
        output='screen',
        parameters=[{
            'geofence_file': '/home/nhio/ros2_ws/lawn_geofence.yaml'
        }]
    )

    return LaunchDescription([
        realsense_node,
        vision_node,
        teleop_stm_node,
        # ntrip_client_node,  # ✅ ปิดไว้เพราะเราจะรันแยกเพื่อ Warm-up
        nmea_gps_node,
        ultrasonic_converter_node,
        rplidar_node,
        auto_datum_node,   # ✅ ตั้งค่า Datum อัตโนมัติจากไฟล์รั้ว
    ])
