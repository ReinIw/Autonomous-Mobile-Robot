#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityInverter(Node):
    def __init__(self):
        super().__init__('velocity_inverter')
        
        # Subscribe dari Teleop/Nav2
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel_raw',
            self.cmd_callback,
            10)
            
        # Publish ke Teensy
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Tameng V2 Aktif! Membalik arah X dan Z secara permanen.")

    def cmd_callback(self, msg):
        inverted_msg = Twist()
        
        # Membalikkan arah Maju/Mundur (Karena I malah mundur)
        inverted_msg.linear.x = msg.linear.x * -1.0 
        
        # Membalikkan arah Kiri/Kanan (Karena J malah Clockwise)
        inverted_msg.angular.z = msg.angular.z * -1.0 
        
        self.publisher.publish(inverted_msg)

def main(args=None):
    rclpy.init(args=args)
    node = VelocityInverter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()