#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowPath
from rclpy.action import ActionClient
from tf2_ros import Buffer, TransformListener
import time
import math
import sys

# ──────────────────────────────────────────────────────────────
#  ค่าพารามิเตอร์การตัดแถว (ปรับได้)
# ──────────────────────────────────────────────────────────────
TURN_ANGLE_THRESHOLD = 1.2   # ~70° - มุมที่ถือว่าเป็น "จุดเลี้ยว"
MIN_CHUNK_LENGTH     = 1.0   # เมตร  - ก้อนที่สั้นกว่านี้จะรวมกับก้อนถัดไป
REST_BETWEEN_CHUNKS  = 2.0   # วินาที - พักหลังจบแต่ละก้อนเพื่อ Reset Error
# ──────────────────────────────────────────────────────────────
 
class MowZigzag(Node):
    def __init__(self):
        super().__init__('mow_zigzag_executor', parameter_overrides=[
            rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        ])
        self.subscription = self.create_subscription(
            Path, '/mowing_path', self.path_callback, 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.action_client = ActionClient(self, FollowPath, 'follow_path')
        self.current_path = None
        self.is_mission_active = False  # 🔒 ล็อคระหว่าง mission
        self._last_path_len = None

        self.get_logger().info("🚜 Mow Zigzag Executor Ready!")
        self.get_logger().info("Waiting for path on /mowing_path...")

    def path_callback(self, msg):
        if self.is_mission_active:
            return  # 🔇 ปิดหูระหว่าง mission ไม่ให้ spam
        self.current_path = msg
        if self._last_path_len != len(msg.poses):
            self._last_path_len = len(msg.poses)
            self.get_logger().info(f"📥 Received new path with {len(msg.poses)} points.")
            self.get_logger().info("To start mowing, please type 'go' in this terminal.")

    def get_robot_pose(self):
        try:
            trans = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = trans.transform.translation.x
            pose.pose.position.y = trans.transform.translation.y
            pose.pose.position.z = trans.transform.translation.z
            pose.pose.orientation = trans.transform.rotation
            return pose
        except Exception:
            return None

    def follow_path_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        state = "[ROTATING]" if feedback.speed < 0.02 else "[MOWING] "
        sys.stdout.write(
            f"\r📉 {state} | Dist: {feedback.distance_to_goal:6.2f}m | Speed: {feedback.speed:.2f}m/s   "
        )
        sys.stdout.flush()

    # ──────────────────────────────────────────────────────────
    #  ฟังก์ชันหลักใหม่: แบ่ง Path เป็นก้อนๆ ตามจุดเลี้ยว
    # ──────────────────────────────────────────────────────────
    def split_into_chunks(self, poses):
        """
        แบ่ง poses ออกเป็นก้อนๆ โดยหั่น "ก่อน" จุดเลี้ยว
        เพื่อให้:
        - แต่ละก้อนจบในพื้นที่เส้นตรง (ไม่จบที่มุม)
        - การเลี้ยวอยู่ที่ "ต้น" ของก้อนถัดไป
        - Controller ไม่เกิดการ Loop ระหว่าง RotationShim กับ PurePursuit
        """
        if len(poses) < 3:
            return [poses]

        # หาตำแหน่งที่ควรหั่น (index ก่อนจุดเลี้ยว)
        cut_indices = []
        for i in range(1, len(poses) - 1):
            p_prev = poses[i - 1].pose.position
            p_curr = poses[i].pose.position
            p_next = poses[i + 1].pose.position

            v1 = (p_curr.x - p_prev.x, p_curr.y - p_prev.y)
            v2 = (p_next.x - p_curr.x, p_next.y - p_curr.y)

            if math.hypot(*v1) < 1e-6 or math.hypot(*v2) < 1e-6:
                continue

            a1 = math.atan2(v1[1], v1[0])
            a2 = math.atan2(v2[1], v2[0])
            diff = abs(a2 - a1)
            if diff > math.pi:
                diff = 2 * math.pi - diff

            if diff > TURN_ANGLE_THRESHOLD:
                # หั่นก่อนจุดเลี้ยว (i-1) ไม่ใช่ที่จุดเลี้ยว (i)
                # เพื่อให้ก้อนปัจจุบันจบในพื้นที่เส้นตรง
                cut_at = max(i - 1, 1)
                if not cut_indices or cut_at > cut_indices[-1] + 5:
                    cut_indices.append(cut_at)

        # สร้าง chunks จาก cut_indices
        chunks = []
        start = 0
        for cut in cut_indices:
            chunk = poses[start:cut + 1]
            if len(chunk) >= 2:
                # ตรวจสอบความยาว
                p0 = chunk[0].pose.position
                pe = chunk[-1].pose.position
                length = math.hypot(pe.x - p0.x, pe.y - p0.y)
                if length >= MIN_CHUNK_LENGTH:
                    chunks.append(chunk)
            start = cut  # chunk ถัดไปเริ่มจากจุดก่อนหน้าเลี้ยว (overlap 1 จุด)

        # เพิ่มก้อนสุดท้าย
        final_chunk = poses[start:]
        if len(final_chunk) >= 2:
            chunks.append(final_chunk)

        return chunks if chunks else [poses]

    def build_path_with_connection(self, from_pose, chunk_poses, path_header):
        """
        สร้าง Path จาก from_pose (ตำแหน่งหุ่นปัจจุบัน) ไปยัง chunk
        เหมือนกับที่ V8-1-4 ทำ: สร้างจุดเชื่อมต่อเพื่อให้ Controller ไม่ ABORT
        """
        now = self.get_clock().now().to_msg()
        path_msg = Path()
        path_msg.header.stamp = now
        path_msg.header.frame_id = 'map'

        first_goal = chunk_poses[0]
        p1 = (from_pose.pose.position.x, from_pose.pose.position.y)
        p2 = (first_goal.pose.position.x, first_goal.pose.position.y)

        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        conn_yaw = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
        num_steps = max(1, int(dist / 0.1))

        for step in range(num_steps):
            alpha = step / float(num_steps)
            cp = PoseStamped()
            cp.header = path_header
            cp.header.stamp = now
            cp.pose.position.x = p1[0] + alpha * (p2[0] - p1[0])
            cp.pose.position.y = p1[1] + alpha * (p2[1] - p1[1])
            cp.pose.position.z = 0.0
            cp.pose.orientation.z = math.sin(conn_yaw / 2.0)
            cp.pose.orientation.w = math.cos(conn_yaw / 2.0)
            path_msg.poses.append(cp)

        # เพิ่ม chunk poses พร้อม timestamp ใหม่
        for pose in chunk_poses:
            pose.header.stamp = now
            pose.header.frame_id = 'map'
            path_msg.poses.append(pose)

        return path_msg

    def send_chunk(self, path_msg, chunk_index, total_chunks):
        """ส่ง Path ก้อนเดียวให้ Nav2 และรอให้เสร็จ"""
        goal_msg = FollowPath.Goal()
        goal_msg.path = path_msg
        goal_msg.controller_id = 'FollowPath'
        goal_msg.goal_checker_id = 'general_goal_checker'

        self.action_client.wait_for_server()
        send_future = self.action_client.send_goal_async(
            goal_msg, feedback_callback=self.follow_path_callback)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().error(f"❌ [Chunk {chunk_index+1}/{total_chunks}] REJECTED by Nav2!")
            return False

        self.get_logger().info(f"✅ [Chunk {chunk_index+1}/{total_chunks}] Accepted — Mowing...")
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()
        print("")  # ขึ้นบรรทัดใหม่หลัง \r
        if result.status == 4:  # SUCCEEDED
            self.get_logger().info(
                f"🏁 [Chunk {chunk_index+1}/{total_chunks}] Completed! "
                f"Resting {REST_BETWEEN_CHUNKS}s to reset error...")
            return True
        else:
            self.get_logger().error(
                f"❌ [Chunk {chunk_index+1}/{total_chunks}] FAILED status={result.status}")
            return False


def main():
    rclpy.init()
    executor_node = MowZigzag()

    while rclpy.ok() and executor_node.current_path is None:
        rclpy.spin_once(executor_node, timeout_sec=0.1)

    path = executor_node.current_path

    try:
        cmd = input(f"\n🚜 [READY] พิกัดทางเดินพร้อมแล้ว! พิมพ์ 'go' แล้วกด Enter เพื่อเริ่มภารกิจ: ").strip().lower()
        # cmd = 'go' # ✅ ล็อคไว้ให้วิ่งอัตโนมัติ (เฉพาะตอนเทสต์ใน Sim)
        if cmd == 'go':
            executor_node.is_mission_active = True # 🔒 เริ่มภารกิจ ล็อคระบบ
            executor_node.get_logger().info("🚀 Starting Mowing Sequence...")

            # 1. หาตำแหน่งเริ่มต้นของหุ่น
            executor_node.get_logger().info("Locating robot in TF map...")
            robot_pose = None
            while rclpy.ok() and robot_pose is None:
                rclpy.spin_once(executor_node, timeout_sec=0.1)
                robot_pose = executor_node.get_robot_pose()
            executor_node.get_logger().info(
                f"Robot found at ({robot_pose.pose.position.x:.2f}, "
                f"{robot_pose.pose.position.y:.2f}).")

            # 2. แบ่ง Path เป็นก้อนๆ
            chunks = executor_node.split_into_chunks(path.poses)
            executor_node.get_logger().info(
                f"📊 Path split into {len(chunks)} chunks. Starting row-by-row mowing...")

            # 3. วนทำทีละก้อน
            executor_node.action_client.wait_for_server()
            executor_node.get_logger().info("FollowPath Action Server is up!")

            current_pose = robot_pose
            for i, chunk_poses in enumerate(chunks):
                # สร้าง Path ก้อนนี้โดย prepend ตำแหน่งหุ่นปัจจุบัน
                path_msg = executor_node.build_path_with_connection(
                    current_pose, chunk_poses, path.header)

                success = executor_node.send_chunk(path_msg, i, len(chunks))

                if not success:
                    executor_node.get_logger().error(f"⚠️ Aborting mission at chunk {i+1}")
                    break

                # พักเพื่อ Reset ค่า Error สะสม
                time.sleep(REST_BETWEEN_CHUNKS)

                # อัปเดตตำแหน่งหุ่นสำหรับก้อนถัดไป
                new_pose = None
                for _ in range(20):
                    rclpy.spin_once(executor_node, timeout_sec=0.1)
                    new_pose = executor_node.get_robot_pose()
                    if new_pose:
                        break
                current_pose = new_pose if new_pose else current_pose

            executor_node.is_mission_active = False # 🔓 จบภารกิจ ปลดล็อค
            executor_node.get_logger().info("🏆 All chunks completed! Mowing Done.")

    except KeyboardInterrupt:
        executor_node.is_mission_active = False
        pass

    executor_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
