#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty, time

# Kecepatan dinaikkan agar menghasilkan ~12.2 RPM di Teensy
LINEAR_SPEED  = 0.4
ANGULAR_SPEED = 0.3

class SafeTeleopTerminal(Node):
    def __init__(self):
        super().__init__('safe_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel_raw', 10)
        
        # Eksekusi pengecekan input pada 20Hz
        self.timer = self.create_timer(0.1, self.publish_loop) 
        
        # Simpan pengaturan terminal asli
        self.settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno()) 
        
        self.last_key_time = time.time()
        self.current_twist = Twist()
        
        self.get_logger().info("=====================================")
        self.get_logger().info("🔥 Terminal Teleop Aktif (Anti-Jeda) 🔥")
        self.get_logger().info(f"Target Kecepatan -> Linear: {LINEAR_SPEED}, Angular: {ANGULAR_SPEED}")
        self.get_logger().info("TAHAN 'w/s/a/d' untuk jalan. LEPAS untuk rem.")
        self.get_logger().info("Tekan Ctrl+C untuk keluar.")
        self.get_logger().info("=====================================")

    def publish_loop(self):
        # Membaca keyboard tanpa memblokir (timeout 0.0 detik)
        if select.select([sys.stdin], [], [], 0.0)[0]:
            key = sys.stdin.read(1)
            self.last_key_time = time.time() # Update timer tiap kali tombol terbaca
            
            if key == 'w':
                self.current_twist.linear.x = LINEAR_SPEED
                self.current_twist.angular.z = 0.0
            elif key == 's':
                self.current_twist.linear.x = -LINEAR_SPEED
                self.current_twist.angular.z = 0.0
            elif key == 'a':
                self.current_twist.linear.x = 0.0
                self.current_twist.angular.z = ANGULAR_SPEED
            elif key == 'd':
                self.current_twist.linear.x = 0.0
                self.current_twist.angular.z = -ANGULAR_SPEED
            elif key == '\x03': # Ctrl+C
                self.restore_terminal()
                sys.exit(0)
        
        # LOGIKA DEAD-MAN'S SWITCH (Waktu tunggu 0.6 detik)
        # 0.6 detik cukup aman untuk mengakomodasi delay auto-repeat dari keyboard OS
        if time.time() - self.last_key_time > 0.6:
            self.current_twist = Twist() 
            
        self.pub.publish(self.current_twist)

    def restore_terminal(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main():
    rclpy.init()
    node = SafeTeleopTerminal()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        node.pub.publish(Twist()) # Kirim stop terakhir kali sebagai safety
        node.restore_terminal()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
