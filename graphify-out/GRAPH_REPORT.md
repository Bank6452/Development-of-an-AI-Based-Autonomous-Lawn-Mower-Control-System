# Graph Report - ros2_ws  (2026-05-08)

## Corpus Check
- 220 files · ~10,642,703 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 831 nodes · 990 edges · 47 communities detected
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 68|Community 68]]

## God Nodes (most connected - your core abstractions)
1. `TopicMonitor` - 27 edges
2. `TeleopSTMNode` - 23 edges
3. `RobotDashboard` - 18 edges
4. `Node` - 17 edges
5. `GeofenceSystem` - 16 edges
6. `GeofenceSystem` - 12 edges
7. `NtripClient` - 11 edges
8. `MowZigzag` - 10 edges
9. `UltrasonicToPointCloud` - 10 edges
10. `setup()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `setup()` --calls--> `initUltrasonic()`  [INFERRED]
  Final_project/Final_Project_Main/src/main.cpp → esp32_bno055_pio/src/ultrasonic.cpp
- `GeofenceSystem` --inherits--> `Node`  [EXTRACTED]
  geofence_enforcer.py → Final_project/ai/yolo_depth_node.py
- `TopicMonitor` --inherits--> `Node`  [EXTRACTED]
  topic_monitor.py → Final_project/ai/yolo_depth_node.py
- `AutoDatumNode` --inherits--> `Node`  [EXTRACTED]
  src/robot_bridge/robot_bridge/auto_datum_node.py → Final_project/ai/yolo_depth_node.py
- `MowZigzag` --inherits--> `Node`  [EXTRACTED]
  src/robot_bridge/robot_bridge/mow_zigzag.py → Final_project/ai/yolo_depth_node.py

## Communities (147 total, 14 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (16): main(), YoloDepthNode, Node, LawnPlanner, main(), main(), VisionNode, LinearCalibrator (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (27): _checkWSAStartup(), clearRxCache(), connect(), CreateSocket(), DGramSocketImpl(), enableNoDelay(), getAddressAsString(), getAddressType() (+19 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (26): clearRxCache(), connect(), CreateSocket(), DGramSocketImpl(), enableNoDelay(), getAddressType(), getPort(), getRawAddress() (+18 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (26): clearRxCache(), connect(), CreateSocket(), DGramSocketImpl(), enableNoDelay(), getAddressType(), getPort(), getRawAddress() (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (24): initBattery(), updateBattery(), getEncoderData(), handleEncoderL(), handleEncoderR(), setupEncoders(), initEngineSystem(), powerOff() (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (12): main(), NtripClient, อ่านข้อมูล NMEA ดิบทจากบอร์ด GPS แล้ว Publish ลง Topic, อ่านข้อมูล NMEA ดิบทจากบอร์ด GPS แล้ว Publish ลง Topic, รับ NMEA (GGA) เพื่อส่งกลับไปให้เซิร์ฟเวอร์ VRS, รับ NMEA (GGA) เพื่อส่งกลับไปให้เซิร์ฟเวอร์ VRS, อ่านข้อมูล RTCM จากเซิร์ฟเวอร์และเขียนลงบอร์ด GPS, อ่านข้อมูล RTCM จากเซิร์ฟเวอร์และเขียนลงบอร์ด GPS (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (4): main(), รับสถานะความปลอดภัยที่ผ่านการตัดสินใจมาแล้วจาก teleop_stm, ใช้สำหรับแสดงระยะวัตถุที่ใกล้ที่สุดเท่านั้น (ไม่ต้องคำนวณ Safety เอง), RobotDashboard

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (18): add_package_runtime_dependencies(), _append_unique_value(), get_commands(), get_packages(), handle_dsv_types_except_source(), _include_comments(), main(), order_packages() (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.2
Nodes (18): add_package_runtime_dependencies(), _append_unique_value(), get_commands(), get_packages(), handle_dsv_types_except_source(), _include_comments(), main(), order_packages() (+10 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (6): clearDTR(), close(), getTermBaudBitmap(), _init(), open(), raw_serial()

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (5): clearDTR(), close(), _init(), open(), raw_serial()

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (10): _getSampleDelayOffsetInDenseMode(), _getSampleDelayOffsetInExpressMode(), _getSampleDelayOffsetInUltraBoostMode(), _getSampleDelayOffsetInUltraDenseMode(), onData(), _onScanNodeCapsuleData(), _onScanNodeDenseCapsuleData(), _onScanNodeUltraCapsuleData() (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (4): GeofenceSystem, main(), เก็บค่า GPS ล่าสุดไว้สำหรับ Record Mode เท่านั้น, ตรวจสอบตำแหน่งหุ่นยนต์จาก TF map->base_link ที่ 10Hz

### Community 15 - "Community 15"
Cohesion: 0.22
Nodes (5): main(), MowZigzag, สร้าง Path จาก from_pose (ตำแหน่งหุ่นปัจจุบัน) ไปยัง chunk         เหมือนกับที่, ส่ง Path ก้อนเดียวให้ Nav2 และรอให้เสร็จ, แบ่ง poses ออกเป็นก้อนๆ โดยหั่น "ก่อน" จุดเลี้ยว         เพื่อให้:         - แต่

### Community 17 - "Community 17"
Cohesion: 0.23
Nodes (7): angleLessThan(), ascendScanData_(), getAngle(), getDistanceQ2(), RawSampleNodeHolder, ScanDataHolder, setAngle()

### Community 18 - "Community 18"
Cohesion: 0.27
Nodes (8): AsyncTransceiver(), _changeBufSize(), cleanData(), fillData(), openChannelAndBind(), ProtocolMessage(), setDataBuf(), unbindAndClose()

### Community 20 - "Community 20"
Cohesion: 0.27
Nodes (3): main(), Temporal Hold Filter (Tuned for JSN-SR04T)         If the sensor goes blind (-1, UltrasonicToPointCloud

### Community 21 - "Community 21"
Cohesion: 0.2
Nodes (6): connect(), createLidarDriver(), createSerialPortChannel(), SerialPortChannel, createTcpChannel(), TcpChannel

### Community 22 - "Community 22"
Cohesion: 0.2
Nodes (8): ILidarDriver(), checkMotorCtrlSupport(), getDeviceInfo(), getHealth(), getLidarIpConf(), getScanDataWithIntervalHq(), getTypicalScanMode(), grabScanDataHq()

### Community 23 - "Community 23"
Cohesion: 0.24
Nodes (5): AutoDatumNode, main(), อ่าน datum จากไฟล์ geofence, เรียกครั้งเดียว (One-shot) หลังจาก 3 วินาที, เช็คผลลัพธ์จาก Service Call

### Community 24 - "Community 24"
Cohesion: 0.2
Nodes (8): บันทึกค่า Offset ลงไฟล์, บันทึกค่า Offset ลงไฟล์, บันทึกค่า Offset ลงไฟล์, บันทึกค่า Offset ลงไฟล์, คำสั่งตั้งค่าหน้าหุ่นให้เป็นทิศเหนือ (0 องศา), คำสั่งตั้งค่าหน้าหุ่นให้เป็นทิศเหนือ (0 องศา), คำสั่งตั้งค่าหน้าหุ่นให้เป็นทิศเหนือ (0 องศา), คำสั่งตั้งค่าหน้าหุ่นให้เป็นทิศเหนือ (0 องศา)

### Community 25 - "Community 25"
Cohesion: 0.2
Nodes (8): ค้นหาพอร์ตอัตโนมัติ (ลองหา CH340 ก่อน ถ้าไม่เจอเอาพอร์ตที่ว่างอยู่), ค้นหาพอร์ตอัตโนมัติ (ลองหา CH340 ก่อน ถ้าไม่เจอเอาพอร์ตที่ว่างอยู่), ค้นหาพอร์ตอัตโนมัติ (ลองหา CH340 ก่อน ถ้าไม่เจอเอาพอร์ตที่ว่างอยู่), ค้นหาพอร์ตอัตโนมัติ (หาเฉพาะ CH340 เท่านั้น), วนลูปตรวจสอบและพยายามเชื่อมต่อพอร์ต USB อัตโนมัติ, วนลูปตรวจสอบและพยายามเชื่อมต่อพอร์ต USB อัตโนมัติ, วนลูปตรวจสอบและพยายามเชื่อมต่อพอร์ต USB อัตโนมัติ, วนลูปตรวจสอบและพยายามเชื่อมต่อพอร์ต USB อัตโนมัติ

### Community 26 - "Community 26"
Cohesion: 0.22
Nodes (8): parse_incoming_data(), ตรวจสอบ Checksum ข้อมูล IMU ที่ส่งมาจาก STM32, ส่งคำสั่งคุมทิศทาง (C) ตามโปรโตคอลใหม่: C,Dir,Speed,Chk     direction: 'F', 'B', ส่งคำสั่งหยุดฉุกเฉิน (E): E,state,chk, แยกแยะข้อมูล I (IMU) และ D (Encoder), send_control_command(), send_emergency(), verify_imu_checksum()

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (4): CreateInstance(), LIDARSampleDataUnpacker(), LIDARSampleDataUnpackerImpl, _registerDataUnpackerHandlers()

### Community 28 - "Community 28"
Cohesion: 0.36
Nodes (5): estimateLength(), exitLoopMode(), onDecodeReset(), onEncodeData(), RPLidarProtocolCodec()

### Community 32 - "Community 32"
Cohesion: 0.29
Nodes (6): วิเคราะห์ข้อมูลจาก LiDAR เพื่อตรวจจับสิ่งกีดขวางด้านหน้า, วิเคราะห์ข้อมูลจาก LiDAR เพื่อตรวจจับสิ่งกีดขวางด้านหน้า, วิเคราะห์ข้อมูลจาก LiDAR เพื่อตรวจจับสิ่งกีดขวางด้านหน้า, วิเคราะห์ข้อมูลจาก LiDAR เพื่อตรวจจับสิ่งกีดขวางด้านหน้า, วิเคราะห์ข้อมูลจาก LiDAR เพื่อตรวจจับสิ่งกีดขวางด้านหน้า, วิเคราะห์ข้อมูลจาก LiDAR เพื่อตรวจจับสิ่งกีดขวางด้านหน้า

### Community 38 - "Community 38"
Cohesion: 0.33
Nodes (4): โหลดค่า Offset จากไฟล์ ถ้าไม่มีให้ใช้ค่า Default (160.0), โหลดค่า Offset จากไฟล์ ถ้าไม่มีให้ใช้ค่า Default (160.0), โหลดค่า Offset จากไฟล์ ถ้าไม่มีให้ใช้ค่า Default (160.0), โหลดค่า Offset จากไฟล์ ถ้าไม่มีให้ใช้ค่า Default (160.0)

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (5): วาดพัดสีแดง/เขียว ใน RViz เพื่อโชว์ระยะปลอดภัยของ LiDAR, วาดพัดสีแดง/เขียว ใน RViz โดยหันไปทางด้านหน้าหุ่นยนต์ (มุม 180 ของ LiDAR), วาดพัดสีแดง/เขียว ใน RViz โดยหันไปทางด้านหน้าหุ่นยนต์ (มุม 180 ของ LiDAR), วาดพัดสีแดง/เขียว ใน RViz โดยหันไปทางด้านหน้าหุ่นยนต์ (มุม 180 ของ LiDAR), วาดพัดสีแดง/เขียว ใน RViz โดยหันไปทางด้านหน้าหุ่นยนต์ (มุม 180 ของ LiDAR)

### Community 40 - "Community 40"
Cohesion: 0.33
Nodes (5): เก็บค่าพิกัดล่าสุดที่ EKF คำนวณเสร็จแล้ว, เก็บค่าพิกัดล่าสุดที่ EKF คำนวณเสร็จแล้ว, เก็บค่าพิกัดล่าสุดที่ EKF คำนวณเสร็จแล้ว, เก็บค่าพิกัดล่าสุดที่ EKF คำนวณเสร็จแล้ว, เก็บค่าพิกัดล่าสุดที่ EKF คำนวณเสร็จแล้ว

### Community 41 - "Community 41"
Cohesion: 0.33
Nodes (5): ยกเลิกงาน Nav2 เมื่อหยุดรอนานเกินไป, ยกเลิกงาน Nav2 เมื่อหยุดรอนานเกินไป, ยกเลิกงาน Nav2 เมื่อหยุดรอนานเกินไป, ยกเลิกงาน Nav2 เมื่อหยุดรอนานเกินไป, ยกเลิกงาน Nav2 เมื่อหยุดรอนานเกินไป

### Community 42 - "Community 42"
Cohesion: 0.6
Nodes (3): colcon_append_unique_value(), colcon_package_source_powershell_script(), colcon_prepend_unique_value()

### Community 44 - "Community 44"
Cohesion: 0.7
Nodes (4): bitrev(), cal(), getResult(), init()

### Community 46 - "Community 46"
Cohesion: 0.4
Nodes (4): รับสัญญาณหยุดฉุกเฉินจาก AI Vision, รับสัญญาณหยุดฉุกเฉินจาก AI Vision, รับสัญญาณหยุดฉุกเฉินจาก AI Vision, รับสัญญาณหยุดฉุกเฉินจาก AI Vision

## Knowledge Gaps
- **78 isolated node(s):** `# NOTE: Using a slightly different mapping to match user's "Pitch is Yaw" observ`, `Find packages based on colcon-specific files created during installation.      :`, `Check the path and if it exists extract the packages runtime dependencies.`, `Order packages topologically.      :param dict packages: A mapping from package`, `Reduce the set of packages to the ones part of the circular dependency.      :pa` (+73 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Node` connect `Community 0` to `Community 5`, `Community 6`, `Community 7`, `Community 13`, `Community 15`, `Community 16`, `Community 19`, `Community 20`, `Community 23`, `Community 29`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `TeleopSTMNode` connect `Community 19` to `Community 0`, `Community 32`, `Community 38`, `Community 39`, `Community 40`, `Community 41`, `Community 46`, `Community 24`, `Community 25`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `TopicMonitor` connect `Community 5` to `Community 0`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **What connects `# NOTE: Using a slightly different mapping to match user's "Pitch is Yaw" observ`, `Find packages based on colcon-specific files created during installation.      :`, `Check the path and if it exists extract the packages runtime dependencies.` to the rest of the system?**
  _78 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._