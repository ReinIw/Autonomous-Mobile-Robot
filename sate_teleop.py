#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

LINEAR_SPEED  = 0.5   # Target max: 4.7 (Dibulatkan 4 RPM di Teensy)
ANGULAR_SPEED = 1.0

class SafeTeleopTerminal(Node):
    def __init__(self):
        super().__init__('safe_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_loop) # Loop stabil di 10Hz
        
        # Simpan settingan asli terminal
        self.settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno()) 
        
        self.get_logger().info("Terminal Teleop Aktif!")
        self.get_logger().info("TAHAN 'w/s/a/d' untuk jalan. LEPAS untuk berhenti.")
        self.get_logger().info("Tekan Ctrl+C untuk keluar.")

    def publish_loop(self):
        key = None
        # Cek apakah ada input keyboard masuk dalam 0.05 detik terakhir
        if select.select([sys.stdin], [], [], 0.05)[0]:
            key = sys.stdin.read(1)

        twist = Twist()
        
        if key == 'w':
            twist.linear.x = LINEAR_SPEED
        elif key == 's':
            twist.linear.x = -LINEAR_SPEED
        elif key == 'a':
            twist.angular.z = ANGULAR_SPEED
        elif key == 'd':
            twist.angular.z = -ANGULAR_SPEED
        elif key == '\x03': # ASCII untuk Ctrl+C
            self.restore_terminal()
            sys.exit(0)
        
        # Jika key == None (jari dilepas / tidak ada input), twist otomatis 0.0 (STOP)
        self.pub.publish(twist)

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
        # Pengereman darurat terakhir sebelum program mati
        node.pub.publish(Twist()) 
        node.restore_terminal()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
