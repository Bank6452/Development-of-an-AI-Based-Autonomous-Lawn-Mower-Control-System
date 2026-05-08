#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker
import yaml
import math
import os
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import rotate

class LawnPlanner(Node):
    def __init__(self):
        super().__init__('lawn_planner')
        
        self.declare_parameter('geofence_file', '/home/nhio/ros2_ws/lawn_geofence.yaml')
        self.declare_parameter('mower_width', 0.40)
        self.declare_parameter('overlap', 0.05)
        
        self.geofence_file = self.get_parameter('geofence_file').get_parameter_value().string_value
        self.mower_width = self.get_parameter('mower_width').get_parameter_value().double_value
        self.overlap = self.get_parameter('overlap').get_parameter_value().double_value
        self.lane_spacing = self.mower_width - self.overlap
        
        self.path_pub = self.create_publisher(Path, '/mowing_path', 10)
        self.marker_pub = self.create_publisher(Marker, '/mowing_markers', 10)
        
        self.timer = self.create_timer(2.0, self.plan_and_publish)
        self.get_logger().info("🚀 Lawn Planner Node Started! (Zig-Zag Mode with Heading)")

    def load_geofence(self):
        if not os.path.exists(self.geofence_file):
            self.get_logger().error(f"❌ Geofence file not found: {self.geofence_file}")
            return None
        
        with open(self.geofence_file, 'r') as f:
            data = yaml.safe_load(f)
            points = data.get('geofence', [])
            if not points: return None
            
            datum_lat = sum(p['lat'] for p in points) / len(points)
            datum_lon = sum(p['lon'] for p in points) / len(points)
            
            lat_to_m = 111320.0
            lon_to_m = 111320.0 * math.cos(math.radians(datum_lat))
            
            poly_points = []
            for p in points:
                x = (p['lon'] - datum_lon) * lon_to_m
                y = (p['lat'] - datum_lat) * lat_to_m
                poly_points.append((x, y))
            
            return Polygon(poly_points)

    def generate_coverage_path(self, polygon):
        if not polygon or polygon.is_empty:
            return []

        best_angle = 0.0
        max_dist = 0.0
        coords = list(polygon.exterior.coords)
        for i in range(len(coords) - 1):
            p1 = coords[i]
            p2 = coords[i+1]
            dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
            if dist > max_dist:
                max_dist = dist
                best_angle = math.degrees(math.atan2(p2[1]-p1[1], p2[0]-p1[0]))

        rotated_poly = rotate(polygon, -best_angle, origin=(0, 0))
        min_x, min_y, max_x, max_y = rotated_poly.bounds
        
        path_points = []
        current_y = min_y + (self.lane_spacing / 2.0)
        reverse = False
        
        while current_y < max_y:
            line = LineString([(min_x - 1, current_y), (max_x + 1, current_y)])
            intersection = rotated_poly.intersection(line)
            
            if not intersection.is_empty:
                if intersection.geom_type == 'LineString':
                    coords = list(intersection.coords)
                    if reverse: coords.reverse()
                    for pt in coords:
                        path_points.append(pt)
                elif intersection.geom_type == 'MultiLineString':
                    lines = sorted(list(intersection.geoms), key=lambda l: l.bounds[0], reverse=reverse)
                    for l in lines:
                        coords = list(l.coords)
                        if reverse: coords.reverse()
                        for pt in coords:
                            path_points.append(pt)
                
                reverse = not reverse
                
            current_y += self.lane_spacing
            
        # 3. Rotate back and densify with heading
        final_points = []
        for i in range(len(path_points) - 1):
            p1_rot = path_points[i]
            p2_rot = path_points[i+1]
            
            dist = math.hypot(p2_rot[0]-p1_rot[0], p2_rot[1]-p1_rot[1])
            resolution = 0.1 # 10cm waypoints
            num_steps = max(1, int(dist / resolution))
            
            for step in range(num_steps):
                alpha = step / float(num_steps)
                ix = p1_rot[0] + alpha * (p2_rot[0] - p1_rot[0])
                iy = p1_rot[1] + alpha * (p2_rot[1] - p1_rot[1])
                
                p_obj = rotate(Point(ix, iy), best_angle, origin=(0, 0))
                
                # Calculate yaw
                next_ix = p1_rot[0] + (step + 1) / float(num_steps) * (p2_rot[0] - p1_rot[0])
                next_iy = p1_rot[1] + (step + 1) / float(num_steps) * (p2_rot[1] - p1_rot[1])
                next_obj = rotate(Point(next_ix, next_iy), best_angle, origin=(0, 0))
                yaw = math.atan2(next_obj.y - p_obj.y, next_obj.x - p_obj.x)
                
                final_points.append((p_obj.x, p_obj.y, yaw))
                
        if path_points:
            last_pt = rotate(Point(path_points[-1]), best_angle, origin=(0, 0))
            last_yaw = final_points[-1][2] if final_points else 0.0
            final_points.append((last_pt.x, last_pt.y, last_yaw))
            
        return final_points

    def plan_and_publish(self):
        poly = self.load_geofence()
        if not poly: return
        
        points = self.generate_coverage_path(poly)
        if not points: return
        
        path_msg = Path()
        path_msg.header.frame_id = "map"
        path_msg.header.stamp = self.get_clock().now().to_msg()
        
        for pt in points:
            pose = PoseStamped()
            pose.header = path_msg.header
            pose.pose.position.x = pt[0]
            pose.pose.position.y = pt[1]
            pose.pose.position.z = 0.0
            
            # Correct orientation from yaw
            yaw = pt[2]
            pose.pose.orientation.z = math.sin(yaw / 2.0)
            pose.pose.orientation.w = math.cos(yaw / 2.0)
            
            path_msg.poses.append(pose)
            
        self.path_pub.publish(path_msg)
        self.get_logger().info(f"📍 Published mowing path with {len(points)} waypoints (with heading)")

def main(args=None):
    rclpy.init(args=args)
    node = LawnPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()ภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภภ
