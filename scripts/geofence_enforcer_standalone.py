#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Int8
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import yaml
import math
import os
import threading
import tf2_ros
import time

class GeofenceSystem(Node):
    def __init__(self, start_mode='enforce'):
        super().__init__('geofence_system')
        
        self.save_path = '/home/nhio/ros2_ws/lawn_geofence.yaml'
        self.safety_margin_meters = 0.05
        self.mode = start_mode 
        
        self.current_fix = None
        self.recorded_lat_lon = []
        self.recorded_points_xy = []
        
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.emergency_pub = self.create_publisher(Int8, '/emergency_stop', 10)
        self.marker_pub = self.create_publisher(Marker, '/geofence_viz', 10)
        self.gps_sub = self.create_subscription(NavSatFix, '/fix', self.gps_callback, 10)

        self.valid_poly = None
        self.polygon_gps = []
        
        if self.mode == 'enforce':
            self.init_enforce_mode()

    def init_enforce_mode(self):
        self.polygon_gps = self.load_geofence()
        if not self.polygon_gps or len(self.polygon_gps) < 3:
            self.get_logger().error(f"❌ โหลดไฟล์รั้วล้มเหลว หรือจุดน้อยกว่า 3 จุด! โปรดรันโปรแกรมใหม่และเลือกโหมดสร้างรั้ว (2)")
            self.valid_poly = None
            return
            
        self.datum_lat = sum(p['lat'] for p in self.polygon_gps) / len(self.polygon_gps)
        self.datum_lon = sum(p['lon'] for p in self.polygon_gps) / len(self.polygon_gps)
        
        self.lat_to_m = 111320.0
        self.lon_to_m = 111320.0 * math.cos(math.radians(self.datum_lat))
        
        polygon_xy = [self.gps_to_enu(p['lat'], p['lon']) for p in self.polygon_gps]
        
        try:
            from shapely.geometry import Polygon
            from shapely.validation import make_valid
            raw_poly = Polygon(polygon_xy)
            self.valid_poly = make_valid(raw_poly)
        except ImportError:
            self.get_logger().error("❌ ไม่พบไลบรารี shapely! กรุณารัน: pip3 install shapely")
            self.valid_poly = None
            return
            
        self.get_logger().info("🛡️ ระบบกันชนรั้วอัตโนมัติ (Enforcer Mode) พร้อมทำงานแล้ว!")
        self.get_logger().info(f"➡️ ระยะเบรกปลอดภัย: {self.safety_margin_meters} เมตร")

    def load_geofence(self):
        if not os.path.exists(self.save_path): return None
        with open(self.save_path, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('geofence', [])

    def save_geofence(self):
        if len(self.recorded_lat_lon) < 3:
            print("⚠️ มีจุดน้อยกว่า 3 จุด ไม่สามารถเป็นรั้วได้! ยกเลิกการบันทึก")
            return False
            
        with open(self.save_path, 'w') as f:
            yaml.dump({'geofence': self.recorded_lat_lon}, f)
        print(f"\n💾 เซฟไฟล์สำเร็จ! ทั้งหมด {len(self.recorded_lat_lon)} จุด ไปที่ {self.save_path}")
        return True

    def gps_to_enu(self, lat, lon):
        x = (lon - self.datum_lon) * self.lon_to_m
        y = (lat - self.datum_lat) * self.lat_to_m
        return (x, y)

    def gps_callback(self, msg):
        self.current_fix = msg
        
        if self.mode == 'record':
            self.publish_marker_record()
            return

        if not self.valid_poly:
            return
            
        x, y = self.gps_to_enu(msg.latitude, msg.longitude)
        
        from shapely.geometry import Point
        point = Point(x, y)
        is_in_bounds = self.valid_poly.contains(point)
        dist_to_edge = self.valid_poly.boundary.distance(point)
        
        stop_msg = Int8()
        if not is_in_bounds:
            self.get_logger().error("🚨 [STOP] นอกเขต! หุ่นยนต์เลยเส้นแดงออกไปแล้ว")
            stop_msg.data = 1
        elif dist_to_edge < self.safety_margin_meters:
            self.get_logger().warn(f"⚠️ [SLOW] เข้าใกล้ขอบเขตอันตราย! ({dist_to_edge:.2f}m)")
            stop_msg.data = 0 
        else:
            stop_msg.data = 0
            
        self.emergency_pub.publish(stop_msg)
        self.publish_marker_enforce()

    def record_point(self):
        if self.current_fix is None:
            print("❌ ยังไม่มีสัญญาณ GPS... กรุณารอสักครู่")
            return

        try:
            now = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform('map', 'base_link', now)
            
            p_x = trans.transform.translation.x
            p_y = trans.transform.translation.y
            
            if self.recorded_points_xy:
                last_p = self.recorded_points_xy[-1]
                dist_m = math.hypot(p_x - last_p.x, p_y - last_p.y)
                if dist_m < 0.05:
                    print(f"⚠️ จุดบันทึกใกล้เกินไป ({dist_m:.2f}m) ขยับรถออกไปอีกนิดครับ (เกิน 20cm)")
                    return

            p_xy = Point()
            p_xy.x = p_x
            p_xy.y = p_y
            p_xy.z = 0.0
            self.recorded_points_xy.append(p_xy)

            point_gps = {
                'lat': self.current_fix.latitude,
                'lon': self.current_fix.longitude,
                'alt': self.current_fix.altitude
            }
            self.recorded_lat_lon.append(point_gps)
            print(f"✅ บันทึกจุดที่ {len(self.recorded_lat_lon)} สำเร็จ! (Lat: {point_gps['lat']:.8f}, Lon: {point_gps['lon']:.8f})")
            self.publish_marker_record()

        except Exception as e:
            print(f"❌ ไม่สามารถระบุตำแหน่งบนแผนที่ได้: {e}")

    def publish_marker_record(self):
        if not self.recorded_points_xy: return
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "geofence"
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.1 
        marker.color.a = 1.0 
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.points = list(self.recorded_points_xy) 
        if len(self.recorded_points_xy) > 1:
             marker.points.append(self.recorded_points_xy[0])
        self.marker_pub.publish(marker)

    def publish_marker_enforce(self):
        try:
            trans = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            rob_map_x = trans.transform.translation.x
            rob_map_y = trans.transform.translation.y
            
            current_x, current_y = self.gps_to_enu(self.current_fix.latitude, self.current_fix.longitude)
            offset_x = rob_map_x - current_x
            offset_y = rob_map_y - current_y
            
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "geofence"
            marker.id = 0
            marker.type = Marker.LINE_STRIP
            marker.action = Marker.ADD
            marker.scale.x = 0.1 
            marker.color.a = 1.0 
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0

            for p in self.polygon_gps:
                px, py = self.gps_to_enu(p['lat'], p['lon'])
                
                p_xy = Point()
                p_xy.x = px + offset_x
                p_xy.y = py + offset_y
                p_xy.z = 0.0
                marker.points.append(p_xy)
                
            if len(marker.points) > 0:
                marker.points.append(marker.points[0])
                
            self.marker_pub.publish(marker)
        except Exception as e:
            pass

def main(args=None):
    rclpy.init(args=args)
    
    print("\n================================")
    print("🛡️ ระบบจัดการรั้วไฟฟ้าอัจฉริยะ (Geofence System - All in One) 🛡️")
    print("1. [Enforce] โหมดกันชน (สแกนแนวรั้วและเบรกอัตโนมัติ)")
    print("2. [Record] โหมดสร้างรั้วใหม่ (เซฟแผนที่ทับของเดิม)")
    print("================================\n")
    
    choice = input("👉 เลือกโหมดทำงาน (1 หรือ 2): ").strip()
    
    mode = 'record' if choice == '2' else 'enforce'
    system = GeofenceSystem(start_mode=mode)
    
    if mode == 'record':
        spin_thread = threading.Thread(target=rclpy.spin, args=(system,), daemon=True)
        spin_thread.start()
        try:
            print("\n🚨 [โหมดสร้างรั้ว] ระบบเบรกถูกปิดชั่วคราว ขับรถหลุดขอบเขตได้อิสระ 🚨")
            while rclpy.ok() and system.mode == 'record':
                val = input("\n💬 ขับไปที่มุมสนาม -> กด [Enter] เพื่อบันทึกจุด (พิมพ์ 's' แล้วกด Enter ค้างไว้เพื่อเซฟ): ").strip().lower()
                if val == 's':
                    if system.save_geofence():
                        print("✅ โหลดแผนที่เข้าสู่สมองกล...")
                        system.mode = 'enforce'
                        system.init_enforce_mode()
                else:
                    system.record_point()
        except KeyboardInterrupt:
            pass
            
    if system.mode == 'enforce':
        print("\n🚀 [โหมดกันชน] หุ่นยนต์พร้อมทำงานและรักษาระยะห่างจากรั้วแล้ว (กด Ctrl+C เพื่อออก) 🚀")
        if 'spin_thread' not in locals(): 
            try:
                rclpy.spin(system)
            except KeyboardInterrupt:
                pass
        else: 
            try:
                while rclpy.ok():
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

    system.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
