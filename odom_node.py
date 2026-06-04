import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math

class OdomNode(Node):
    def __init__(self):
        super().__init__('odom_node')
        
        # Subscribe ke data mentah jarak roda dari Teensy
        self.sub = self.create_subscription(
            Float32MultiArray, 
            '/wheel_travel', 
            self.encoder_callback, 
            10
        )
        
        # Publisher untuk standar Nav2
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # --- KONFIGURASI MEKANIK ROBOT ---
        # Jarak mekanis dari titik tengah tapak roda kiri ke kanan (dalam satuan meter)
        # SILAKAN UBAH ANGKA INI SESUAI UKURAN FISIK AMR KAMU AGAR PRESISI
        self.wheel_base = 0.55 
        
        # Variabel State Koordinat Global
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        
        self.last_l_travel = 0.0
        self.last_r_travel = 0.0
        self.last_time = self.get_clock().now()
        self.first_reading = True

    def quaternion_from_euler(self, roll, pitch, yaw):
        """Fungsi pembantu untuk mengubah sudut Euler (Yaw) menjadi Quaternion untuk ROS 2"""
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        q = [0.0]*4
        q[0] = cy * cp * sr - sy * sp * cr
        q[1] = sy * cp * sr + cy * sp * cr
        q[2] = sy * cp * cr - cy * sp * sr
        q[3] = cy * cp * cr + sy * sp * sr
        return q

    def encoder_callback(self, msg):
        current_time = self.get_clock().now()
        
        # Pastikan data yang masuk valid (minimal ada 2 data: kiri dan kanan)
        if len(msg.data) < 2:
            return
            
        l_travel = msg.data[0]
        r_travel = msg.data[1]
        
        # Setup awal untuk mendapatkan nilai referensi pertama
        if self.first_reading:
            self.last_l_travel = l_travel
            self.last_r_travel = r_travel
            self.last_time = current_time
            self.first_reading = False
            return
            
        # 1. Hitung Delta Jarak Roda (meter)
        dl = l_travel - self.last_l_travel
        dr = r_travel - self.last_r_travel
        
        # 2. Hitung Delta Waktu (detik)
        dt = (current_time.nanoseconds - self.last_time.nanoseconds) / 1e9
        if dt <= 0:
            return
            
        # 3. Kinematika Differential Drive
        dc = (dl + dr) / 2.0
        dc = dc * -1.0 
        dth = (dr - dl) / self.wheel_base * -1.0
        # 4. Update Posisi Global Robot
        self.x += dc * math.cos(self.th + dth / 2.0)
        self.y += dc * math.sin(self.th + dth / 2.0)
        self.th += dth
        
        # 5. Kecepatan Saat Ini
        v = dc / dt
        w = dth / dt
        
        # --- BENTUK PESAN ODOMETRY ---
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        
        q = self.quaternion_from_euler(0.0, 0.0, self.th)
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        
        odom.twist.twist.linear.x = v
        odom.twist.twist.angular.z = w
        
        # Publish topik /odom
        self.odom_pub.publish(odom)
        
        # --- BENTUK PESAN TRANSFORM (TF) ---
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        # Publish TF
        # self.tf_broadcaster.sendTransform(t)
        
        # Update State untuk putaran berikutnya
        self.last_l_travel = l_travel
        self.last_r_travel = r_travel
        self.last_time = current_time

def main(args=None):
    rclpy.init(args=args)
    node = OdomNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
