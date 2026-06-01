#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelInverter(Node):
    def __init__(self):
        super().__init__('cmd_vel_inverter')
        
        # Mencegat perintah murni dari Teleop / Nav2
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel_raw',
            self.cmd_callback,
            10)
            
        # Mengirimkan perintah yang sudah disilang ke Teensy
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Tameng Inverter Aktif! Melindungi Teensy dari arah terbalik.")

    def cmd_callback(self, msg):
        inverted_msg = Twist()
        
        # Linear tetap maju/mundur normal
        inverted_msg.linear.x = msg.linear.x 
        
        # --- INI INTI MANUVERNYA ---
        # Sudut kemudi dikali -1 agar Teensy (yang logikanya terbalik) merespons dengan benar
        inverted_msg.angular.z = msg.angular.z * -1.0 
        
        self.publisher.publish(inverted_msg)

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelInverter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()