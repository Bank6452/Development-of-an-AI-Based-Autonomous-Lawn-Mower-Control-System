#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data
import cv2
import numpy as np
from ultralytics import YOLO
import torch
import time

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        
        # --- Parameters ---
        self.declare_parameter('model_path', 'yolo11n.pt')
        self.declare_parameter('stop_distance', 2.0)
        self.declare_parameter('fence_distance', 1.0)
        
        self.stop_dist = self.get_parameter('stop_distance').get_parameter_value().double_value
        self.fence_dist = self.get_parameter('fence_distance').get_parameter_value().double_value
        
        # --- YOLO Setup ---
        model_name = self.get_parameter('model_path').get_parameter_value().string_value
        self.get_logger().info(f"🚀 Loading YOLO Model: {model_name}...")
        
        if torch.cuda.is_available():
            self.device = 'cuda:0'
        else:
            self.device = 'cpu'
            
        self.model = YOLO(model_name)
        self.model.to(self.device)
        
        self.bridge = CvBridge()
        self.latest_depth = None
        self.is_processing = False
        
        # --- ROS2 Sub/Pub ---
        self.depth_sub = self.create_subscription(
            Image, '/camera/camera/depth/image_rect_raw', self.depth_callback, qos_profile_sensor_data)
        self.color_sub = self.create_subscription(
            Image, '/camera/camera/color/image_raw', self.color_callback, qos_profile_sensor_data)
        
        self.stop_pub = self.create_publisher(String, '/cmd_emergency', 10)
        self.debug_img_pub = self.create_publisher(Image, '/camera/yolo/debug_image', 10)
        self.perf_pub = self.create_publisher(String, '/camera/yolo/performance', 10)
        
        self.get_logger().info(f"✅ AI Safety Active (Ignoring Plants Mode)")

    def depth_callback(self, msg):
        try:
            self.latest_depth = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        except:
            pass

    def color_callback(self, msg):
        if self.is_processing or self.latest_depth is None:
            return

        self.is_processing = True
        t_start = time.time()
        
        try:
            original_header = msg.header
            color_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            h, w = color_image.shape[:2]
            
            # --- 1. AI Object Detection First ---
            # เราต้องรัน AI ก่อนเพื่อหาว่าตรงไหนคือ "พืช" จะได้เอาไปหักลบออกจาก Depth Fence
            results = self.model(color_image, conf=0.4, verbose=False, imgsz=320, device=self.device)[0]
            t_after_yolo = time.time()
            
            # สร้าง Mask สำหรับพื้นที่ที่เราจะ "ยกเว้น" (เช่น ต้นไม้)
            ignore_mask = np.zeros((h, w), dtype=np.uint8)
            
            ai_danger_detected = False
            
            for box in results.boxes:
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # 🌿 ถ้าเป็นพืช (potted plant) ให้ถมสีขาวใน Mask เพื่อ "ข้าม" การตรวจจับระยะทาง
                if label == 'potted plant':
                    cv2.rectangle(ignore_mask, (x1, y1), (x2, y2), 255, -1)
                    
                    # 🛑 ถ้าเป็น คน/หมา/แมว ให้เช็คระยะเพื่อสั่งหยุด
                elif label in ['person', 'dog', 'cat']:
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    if cy < h and cx < w:
                        dist_m = self.latest_depth[cy, cx] / 1000.0
                        if dist_m < 2.0:
                            ai_danger_detected = True
            
            # --- 2. Depth Safety Fence (พร้อมระบบข้ามต้นไม้) ---
            roi_x1, roi_x2 = int(w*0.0), int(w*1.0)
            roi_y1, roi_y2 = int(h*0.4), int(h*0.9)
            
            depth_roi = self.latest_depth[roi_y1:roi_y2, roi_x1:roi_x2].copy()
            mask_roi = ignore_mask[roi_y1:roi_y2, roi_x1:roi_x2]
            
            # ✂️ ลบพื้นที่ที่เป็นต้นไม้ออก (เซ็ตระยะทางให้เป็นค่าไกลๆ เพื่อไม่ให้เบรก)
            depth_roi[mask_roi > 0] = 5000 # 5 เมตร (ถือว่าปลอดภัย)
            
            valid_mask = depth_roi > 100
            close_points = depth_roi[valid_mask & (depth_roi < self.fence_dist * 1000)]
            
            fence_triggered = False
            fence_color = (0, 255, 0)
            if len(close_points) > 1500:
                fence_triggered = True
                fence_color = (0, 0, 255)
                avg_dist = np.mean(close_points) / 1000.0
                cv2.putText(color_image, f"FENCE STOP: {avg_dist:.2f}m", (10, roi_y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # --- 3. Visualization & Publishing ---
            annotated_frame = results.plot()
            cv2.rectangle(annotated_frame, (roi_x1, roi_y1), (roi_x2, roi_y2), fence_color, 2)
            
            if fence_triggered or ai_danger_detected:
                self.stop_pub.publish(String(data="E,1"))
            else:
                self.stop_pub.publish(String(data="E,0"))

            small_frame = cv2.resize(annotated_frame, (320, 240))
            debug_msg = self.bridge.cv2_to_imgmsg(small_frame, "bgr8")
            debug_msg.header = original_header
            self.debug_img_pub.publish(debug_msg)
            
            t_end = time.time()
            fps = 1.0 / (t_end - t_start)
            yolo_ms = (t_after_yolo - t_start) * 1000
            perf_msg = String()
            perf_msg.data = f"{fps:.1f} FPS | AI: {yolo_ms:.1f}ms"
            self.perf_pub.publish(perf_msg)

        except Exception as e:
            self.get_logger().error(f"Error: {e}")
        finally:
            self.is_processing = False

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
